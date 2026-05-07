# Py2Deb

# 🚀 Py2Deb - Python to .deb Package Builder

**Py2Deb** is a powerful and user-friendly GUI tool built with Python and Tkinter that allows developers to convert their Python scripts into `.deb` packages effortlessly. Whether you're building utilities for distribution or testing deployment pipelines, Py2Deb simplifies the packaging process into a few intuitive clicks.

---

## ✨ Features

- 📂 Select any `.py` or `.sh` script and package it as a `.deb`
- 🖼 Optional icon file embedding
- 🛠 Easy configuration of control fields (Package Name, Version, Maintainer, etc.)
- ⚙️ Autostart and Run-on-Install options *(coming soon)*
- 🧹 Cleanup build files after packaging
- 📄 Live build output with error/success highlighting
- 🎨 Modern and responsive Tkinter GUI

---

## 📦 What is a `.deb` Package?

A `.deb` file is a Debian software package used by distributions such as Ubuntu, Kali Linux, and others. Py2Deb automatically creates the Debian package structure, control files, and post-install scripts if necessary.

---


---

## 🔧 Requirements

- Python 3.6+
- Linux-based OS (Debian/Ubuntu/Kali/etc.)
- `dpkg`, `fakeroot`, `chmod`, `cp`, and `desktop-file-validate` (usually pre-installed on most distros)

Install dependencies:

```bash
sudo apt update
sudo apt install python3-tk fakeroot dpkg-dev


## 🚀 How to Use
Clone the repo:

git clone https://github.com/yourusername/py2deb.git
cd py2deb
Run the GUI:


python3 py2deb_gui.py
Steps inside the GUI:

Click on 📂 Select Python File and choose your .py script.

(Optional) Click on 🖼 Select Icon File (.png, .svg, etc.).

Fill in fields like package name, version, etc.

Click 🛠 Build .deb Package

Done! Your .deb file will be generated and saved in the dist/ folder.

##📁 Output Structure
After building, the structure looks like:


###mypackage_1.0_amd64.deb
dist/
└── mypackage/
    ├── DEBIAN/
    │   ├── control
    │   ├── postinst
    ├── usr/
    │   ├── bin/
    │   └── share/applications/
    └── opt/

🧪 Example Use Cases
✅ Deploying internal Python automation tools

✅ Sharing command-line or GUI utilities without exposing source code

✅ Creating .deb packages for private/internal Linux deployments

✅ Running custom post-install scripts (e.g., service setup, environment config)

✅ Simulating .deb-based attack vectors in a safe lab

✅ Studying Linux .deb trust exploitation techniques for defense

✅ Red Team operations in isolated environments to test EDR/AV response

✅ Teaching cybersecurity students how attackers might abuse package trust

⚠️ Ethical Notice
This tool is intended only for educational, research, and authorized security testing in isolated lab environments. Do not use it on unauthorized systems or for malicious purposes. Misuse may violate laws and ethical standards. Always operate under proper legal permission.


🧑‍💻 Author
Varun
Ethical Hacker & Cybersecurity Researcher
LinkedIn - www.linkedin.com/in/mr-pentest
