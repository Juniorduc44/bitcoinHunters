

# Standard Operating Procedures (SOPs) for Steganography Tools(Linux Edition)

This guide provides quick steps for using `steghide` and `stegseek` to crack passwords, create steganographic JPEG files, and extract hidden data.

---

## 1. Crack Password with `stegseek`

**Objective:** Find the password for a `steghide`-protected JPEG using a wordlist.

**Command:**
```bash
stegseek <stego_file.jpg> <wordlist.txt>
```

**Steps:**
1. Place the steganographic JPEG (e.g., `stego.jpg`) and a wordlist (e.g., `wordlist.txt`) in your directory.
2. Run:  
   ```bash
   stegseek stego.jpg wordlist.txt
   ```
3. If successful, the password is displayed, and data is extracted (e.g., `stego.jpg.out`).

**Notes:**
- Use a good wordlist for better chances.

---

## 2. Create a Steganographic File with `steghide`

**Objective:** Hide a text file in a JPEG image.

**Command:**
```bash
steghide embed -cf <cover_file.jpg> -ef <embed_file.txt> -sf <output_stego.jpg> -p "<password>"
```

**Steps:**
1. Prepare a cover image (e.g., `cover.jpg`) and a file to hide (e.g., `secret.txt`).
2. Run:  
   ```bash
   steghide embed -cf cover.jpg -ef secret.txt -sf stego.jpg -p "mypassword"
   ```
3. Output is `stego.jpg` with hidden data.

**Notes:**
- Ensure the cover image is large enough.

---

## 3. Extract Hidden Data with `steghide`

**Objective:** Retrieve hidden data from a steganographic JPEG.

**Command:**
```bash
steghide extract -sf <stego_file.jpg> -xf <output_file.txt>
```

**Steps:**
1. Place the steganographic file (e.g., `stego.jpg`) in your directory.
2. Run:  
   ```bash
   steghide extract -sf stego.jpg -xf output.txt
   ```
3. Enter the password when prompted.

**With Known Password:**
- Add `-p`:  
  ```bash
  steghide extract -sf stego.jpg -xf output.txt -p "mypassword"
  ```

**Notes:**
- Use `stegseek` if the password is unknown.

---

## 4. Check for Hidden Data

**Command:**
```bash
steghide info -sf <stego_file.jpg>
```

**Steps:**
1. Run:  
   ```bash
   steghide info -sf stego.jpg
   ```
2. Enter the password to see details.

---

## Quick Reference

| Task                  | Command Example                                      |
|-----------------------|-----------------------------------------------------|
| Crack password        | `stegseek stego.jpg wordlist.txt`                  |
| Create stego file     | `steghide embed -cf cover.jpg -ef secret.txt -sf stego.jpg -p "mypassword"` |
| Extract data          | `steghide extract -sf stego.jpg -xf output.txt -p "mypassword"` |
| Check for data        | `steghide info -sf stego.jpg`                      |

