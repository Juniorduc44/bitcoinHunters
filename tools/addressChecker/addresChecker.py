import os
import time
import hashlib
import threading
import requests
import customtkinter as ctk
from bitcoinlib.keys import Key
from bitcoinlib.wallets import Wallet
import bitcoinlib.wallets

# Set appearance mode and default color theme
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class BlockchainAPIManager:
    """Class to manage blockchain API services for balance checking"""
    
    def __init__(self):
        # Using only the most reliable APIs
        self.apis = [
            {
                "name": "Blockchain.info",
                "url": "https://blockchain.info/balance?active={address}",
                "parser": self._parse_blockchain_info
            },
            {
                "name": "BlockCypher",
                "url": "https://api.blockcypher.com/v1/btc/main/addrs/{address}/balance",
                "parser": self._parse_blockcypher
            }
        ]
        self.current_api_index = 0
        
    def _parse_blockchain_info(self, response):
        data = response.json()
        address = list(data.keys())[0]
        balance_satoshis = data[address]["final_balance"]
        return balance_satoshis / 100000000  # Convert satoshis to BTC

    def _parse_blockcypher(self, response):
        data = response.json()
        return data["final_balance"] / 100000000

    def get_next_api(self):
        """Get the next API in the rotation"""
        api = self.apis[self.current_api_index]
        self.current_api_index = (self.current_api_index + 1) % len(self.apis)
        return api

    def check_balance(self, address, max_retries=3):
        """Check balance using the available APIs with retries"""
        for retry in range(max_retries):
            for api in self.apis:
                api_name = api["name"]
                try:
                    url = api["url"].format(address=address)
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        balance = api["parser"](response)
                        return balance, api_name
                except Exception:
                    continue
            time.sleep(1)
        return 0, "Failed (API Error)"

class WalletGeneratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Bitcoin Wallet Generator")
        self.geometry("900x600")
        self.file_path = None
        self.is_processing = False
        self.mode = ctk.StringVar(value="line")
        self.app_function = ctk.StringVar(value="brain_wallet")  # New variable for function selection
        self.api_delay = ctk.DoubleVar(value=1.5)
        self.api_manager = BlockchainAPIManager()
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(main_frame, text="Bitcoin Wallet Generator", 
                                  font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=10)
        
        desc_text = "This application processes Bitcoin-related operations from text file input."
        desc_label = ctk.CTkLabel(main_frame, text=desc_text, 
                                 font=ctk.CTkFont(size=14))
        desc_label.pack(pady=5)
        
        # Function selection frame with radio buttons
        function_frame = ctk.CTkFrame(main_frame)
        function_frame.pack(fill=ctk.X, padx=20, pady=10)
        
        function_label = ctk.CTkLabel(function_frame, text="Function:", 
                                    font=ctk.CTkFont(size=14, weight="bold"))
        function_label.pack(side=ctk.LEFT, padx=10)
        
        brain_wallet_radio = ctk.CTkRadioButton(function_frame, text="Brain Wallet", 
                                              variable=self.app_function, value="brain_wallet",
                                              command=self.update_ui_for_function)
        brain_wallet_radio.pack(side=ctk.LEFT, padx=20)
        
        address_checker_radio = ctk.CTkRadioButton(function_frame, text="BTC Address Checker", 
                                                variable=self.app_function, value="address_checker",
                                                command=self.update_ui_for_function)
        address_checker_radio.pack(side=ctk.LEFT, padx=20)
        
        # Create frames for different function modes
        self.brain_wallet_frame = ctk.CTkFrame(main_frame)
        self.address_checker_frame = ctk.CTkFrame(main_frame)
        
        # Brain wallet mode-specific UI
        mode_frame = ctk.CTkFrame(self.brain_wallet_frame)
        mode_frame.pack(fill=ctk.X, padx=20, pady=10)
        
        mode_label = ctk.CTkLabel(mode_frame, text="Input Mode:", 
                                 font=ctk.CTkFont(size=14, weight="bold"))
        mode_label.pack(side=ctk.LEFT, padx=10)
        
        tuple_radio = ctk.CTkRadioButton(mode_frame, text="Tuple Mode (comma-separated values)", 
                                        variable=self.mode, value="tuple")
        tuple_radio.pack(side=ctk.LEFT, padx=20)
        
        line_radio = ctk.CTkRadioButton(mode_frame, text="Line-by-Line Mode", 
                                      variable=self.mode, value="line")
        line_radio.pack(side=ctk.LEFT, padx=20)
        
        self.mode_desc = ctk.CTkLabel(self.brain_wallet_frame, text=self.get_mode_description("line"), 
                                    font=ctk.CTkFont(size=12), wraplength=700)
        self.mode_desc.pack(pady=5)
        
        self.mode.trace_add("write", self.update_mode_description)
        
        # Address checker mode-specific UI
        address_mode_frame = ctk.CTkFrame(self.address_checker_frame)
        address_mode_frame.pack(fill=ctk.X, padx=20, pady=10)
        
        # We'll reuse the same mode variable for consistency
        address_mode_label = ctk.CTkLabel(address_mode_frame, text="Address Input Mode:", 
                                        font=ctk.CTkFont(size=14, weight="bold"))
        address_mode_label.pack(side=ctk.LEFT, padx=10)
        
        address_tuple_radio = ctk.CTkRadioButton(address_mode_frame, text="Comma-separated Addresses", 
                                              variable=self.mode, value="tuple")
        address_tuple_radio.pack(side=ctk.LEFT, padx=20)
        
        address_line_radio = ctk.CTkRadioButton(address_mode_frame, text="One Address Per Line", 
                                             variable=self.mode, value="line")
        address_line_radio.pack(side=ctk.LEFT, padx=20)
        
        self.address_mode_desc = ctk.CTkLabel(self.address_checker_frame, 
                                           text="One Address Per Line: Process each line as a separate Bitcoin address.", 
                                           font=ctk.CTkFont(size=12), wraplength=700)
        self.address_mode_desc.pack(pady=5)
        
        # Common UI elements
        delay_frame = ctk.CTkFrame(main_frame)
        delay_frame.pack(fill=ctk.X, padx=20, pady=10)
        
        delay_label = ctk.CTkLabel(delay_frame, text="API Request Delay (sec):", 
                                  font=ctk.CTkFont(size=14, weight="bold"))
        delay_label.pack(side=ctk.LEFT, padx=10)
        
        delay_slider = ctk.CTkSlider(delay_frame, from_=0.5, to=5.0, variable=self.api_delay,
                                   width=200)
        delay_slider.pack(side=ctk.LEFT, padx=10)
        
        self.delay_value_label = ctk.CTkLabel(delay_frame, text="1.5")
        self.delay_value_label.pack(side=ctk.LEFT, padx=5)
        
        self.api_delay.trace_add("write", self.update_delay_label)
        
        file_frame = ctk.CTkFrame(main_frame)
        file_frame.pack(fill=ctk.X, padx=20, pady=10)
        
        file_label = ctk.CTkLabel(file_frame, text="Input File:", 
                                 font=ctk.CTkFont(size=14, weight="bold"))
        file_label.pack(side=ctk.LEFT, padx=10)
        
        self.file_path_var = ctk.StringVar()
        file_entry = ctk.CTkEntry(file_frame, textvariable=self.file_path_var, width=400)
        file_entry.pack(side=ctk.LEFT, padx=10, fill=ctk.X, expand=True)
        
        browse_button = ctk.CTkButton(file_frame, text="Browse", command=self.browse_file)
        browse_button.pack(side=ctk.LEFT, padx=10)
        
        self.process_button = ctk.CTkButton(main_frame, text="Generate Wallets", 
                                          command=self.start_processing, height=40)
        self.process_button.pack(pady=20)
        
        progress_frame = ctk.CTkFrame(main_frame)
        progress_frame.pack(fill=ctk.X, padx=20, pady=10)
        
        self.progress_label = ctk.CTkLabel(progress_frame, text="Ready", 
                                         font=ctk.CTkFont(size=12))
        self.progress_label.pack(side=ctk.LEFT, padx=10)
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame, width=400)
        self.progress_bar.pack(side=ctk.LEFT, padx=10, fill=ctk.X, expand=True)
        self.progress_bar.set(0)
        
        results_label = ctk.CTkLabel(main_frame, text="Results:", 
                                    font=ctk.CTkFont(size=14, weight="bold"))
        results_label.pack(anchor=ctk.W, padx=20, pady=(10, 5))
        
        text_frame = ctk.CTkFrame(main_frame)
        text_frame.pack(fill=ctk.BOTH, expand=True, padx=20, pady=10)
        
        self.results_text = ctk.CTkTextbox(text_frame, wrap=ctk.WORD, font=ctk.CTkFont(family="Courier", size=12))
        self.results_text.pack(fill=ctk.BOTH, expand=True)
        
        # Correctly configure color tags using tag_config
        self.results_text.tag_config("red", foreground="red")
        self.results_text.tag_config("green", foreground="green")
        
        self.status_var = ctk.StringVar(value="Ready")
        status_bar = ctk.CTkLabel(self, textvariable=self.status_var, 
                                 font=ctk.CTkFont(size=12))
        status_bar.pack(side=ctk.BOTTOM, fill=ctk.X, padx=10, pady=5)
        
        # Initialize UI state
        self.update_ui_for_function()
    
    def update_ui_for_function(self):
        """Update UI elements based on selected function"""
        function = self.app_function.get()
        
        # Hide both frames first
        self.brain_wallet_frame.pack_forget()
        self.address_checker_frame.pack_forget()
        
        if function == "brain_wallet":
            self.brain_wallet_frame.pack(fill=ctk.X, padx=20, pady=5)
            self.process_button.configure(text="Generate Wallets")
            self.update_mode_description()  # Update brain wallet mode description
        else:  # address_checker
            self.address_checker_frame.pack(fill=ctk.X, padx=20, pady=5)
            self.process_button.configure(text="Check Addresses")
            self.update_address_mode_description()  # Update address checker mode description
    
    def update_address_mode_description(self):
        """Update the description for address checker mode"""
        mode = self.mode.get()
        if mode == "tuple":
            desc = "Comma-separated Addresses: Process multiple addresses separated by commas."
        else:  # line
            desc = "One Address Per Line: Process each line as a separate Bitcoin address."
        self.address_mode_desc.configure(text=desc)
    
    def get_mode_description(self, mode):
        descriptions = {
            "tuple": "Tuple Mode: Reads comma-separated values from the file, processing each value as a separate wallet.",
            "line": "Line-by-Line Mode: Processes each line as a single input, allowing commas within the text."
        }
        return descriptions.get(mode, "")
    
    def update_mode_description(self, *args):
        self.mode_desc.configure(text=self.get_mode_description(self.mode.get()))
        # Also update address mode description if that view is active
        if self.app_function.get() == "address_checker":
            self.update_address_mode_description()
    
    def update_delay_label(self, *args):
        self.delay_value_label.configure(text=f"{self.api_delay.get():.1f}")
    
    def browse_file(self):
        file_path = ctk.filedialog.askopenfilename(
            title="Select Input File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
    
    def start_processing(self):
        if self.is_processing:
            return
        
        file_path = self.file_path_var.get().strip()
        if not file_path:
            self.show_error("Please select an input file.")
            return
        
        if not os.path.exists(file_path):
            self.show_error(f"File not found: {file_path}")
            return
        
        self.results_text.delete("1.0", ctk.END)
        self.is_processing = True
        self.process_button.configure(state=ctk.DISABLED, text="Processing...")
        self.status_var.set("Processing...")
        
        function = self.app_function.get()
        
        if function == "brain_wallet":
            processing_thread = threading.Thread(target=self.process_brain_wallet_file, args=(file_path,))
        else:  # address_checker
            processing_thread = threading.Thread(target=self.process_address_file, args=(file_path,))
        
        processing_thread.daemon = True
        processing_thread.start()
    
    def process_brain_wallet_file(self, file_path):
        """Process the file for brain wallet generation"""
        try:
            mode = self.mode.get()
            api_delay = self.api_delay.get()
            
            if mode == "tuple":
                variations = self.read_tuple_variations(file_path)
            else:
                variations = self.read_line_variations(file_path)
            
            if not variations:
                self.log_result("Error: The file is empty or contains no valid entries.", "red")
                self.finish_processing()
                return
            
            total_variations = len(variations)
            self.update_progress_label(f"Processing 0/{total_variations}")
            
            for i, variation in enumerate(variations):
                progress_value = (i + 1) / total_variations
                self.update_progress(progress_value)
                self.update_progress_label(f"Processing {i + 1}/{total_variations}")
                
                wallet_name = f"wallet_{i:02d}"
                
                try:
                    bitcoinlib.wallets.wallet_delete_if_exists(wallet_name)
                except Exception:
                    pass
                
                hash_object = hashlib.sha256(variation.encode())
                private_key_hex = hash_object.hexdigest()
                
                try:
                    key = Key(private_key_hex)
                    address = key.address()
                    
                    # Log processing attempt in red
                    self.log_result(f"Processing: '{variation}' -> Address: {address}", "red")
                    
                    time.sleep(api_delay)
                    
                    balance, api_used = self.api_manager.check_balance(address)
                    
                    balance_status = "CONGRATS***************greater than 0!!!!!!!!!!!!!!!!!!!!!!!!" if balance > 0 else "0"
                    
                    result = (f"{wallet_name}: Hashed: '{variation}' -> "
                              f"Private Key: {private_key_hex} -> "
                              f"Legacy Address: {address} -> "
                              f"Balance: {balance} BTC (via {api_used}) -> "
                              f"Status: {balance_status}")
                    tag = "green" if balance > 0 else "red"
                    self.log_result(result, tag)
                
                except Exception as e:
                    error_msg = f"{wallet_name}: Error processing private key: {str(e)}"
                    self.log_result(error_msg, "red")
            
            # Log completion in red (not a balance result)
            self.log_result("\nProcessing completed successfully!", "red")
        
        except Exception as e:
            self.log_result(f"Error: An unexpected issue occurred: {str(e)}", "red")
        
        finally:
            self.finish_processing()
    
    def process_address_file(self, file_path):
        """Process the file for direct address checking"""
        try:
            mode = self.mode.get()
            api_delay = self.api_delay.get()
            
            if mode == "tuple":
                addresses = self.read_tuple_variations(file_path)
            else:
                addresses = self.read_line_variations(file_path)
            
            if not addresses:
                self.log_result("Error: The file is empty or contains no valid addresses.", "red")
                self.finish_processing()
                return
            
            total_addresses = len(addresses)
            self.update_progress_label(f"Checking 0/{total_addresses}")
            
            for i, address in enumerate(addresses):
                progress_value = (i + 1) / total_addresses
                self.update_progress(progress_value)
                self.update_progress_label(f"Checking {i + 1}/{total_addresses}")
                
                # Remove any leading/trailing whitespace from the address
                address = address.strip()
                
                # Log processing attempt
                self.log_result(f"Checking address: {address}", "red")
                
                try:
                    time.sleep(api_delay)
                    
                    balance, api_used = self.api_manager.check_balance(address)
                    
                    balance_status = "CONGRATS***************greater than 0!!!!!!!!!!!!!!!!!!!!!!!!" if balance > 0 else "0"
                    
                    result = (f"Address: {address} -> "
                              f"Balance: {balance} BTC (via {api_used}) -> "
                              f"Status: {balance_status}")
                    tag = "green" if balance > 0 else "red"
                    self.log_result(result, tag)
                
                except Exception as e:
                    error_msg = f"Error checking address {address}: {str(e)}"
                    self.log_result(error_msg, "red")
            
            # Log completion
            self.log_result("\nAddress checking completed successfully!", "red")
        
        except Exception as e:
            self.log_result(f"Error: An unexpected issue occurred: {str(e)}", "red")
        
        finally:
            self.finish_processing()
    
    def read_tuple_variations(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()
            variations = [var.strip() for var in content.split(',') if var.strip()]
        return variations
    
    def read_line_variations(self, file_path):
        with open(file_path, 'r') as file:
            variations = [line.strip() for line in file if line.strip()]
        return variations
    
    def log_result(self, message, tag="red"):
        """Log a message to the results text box with a specified color tag, defaulting to red."""
        self.results_text.insert(ctk.END, message + "\n", tag)
        self.results_text.see(ctk.END)
    
    def update_progress(self, value):
        self.progress_bar.set(value)
    
    def update_progress_label(self, text):
        self.progress_label.configure(text=text)
    
    def finish_processing(self):
        self.is_processing = False
        if self.app_function.get() == "brain_wallet":
            button_text = "Generate Wallets"
        else:
            button_text = "Check Addresses"
        self.process_button.configure(state=ctk.NORMAL, text=button_text)
        self.status_var.set("Ready")
        self.update_progress(1.0)
        self.update_progress_label("Complete")
    
    def show_error(self, message):
        self.log_result(f"Error: {message}", "red")

if __name__ == "__main__":
    app = WalletGeneratorApp()
    app.mainloop()