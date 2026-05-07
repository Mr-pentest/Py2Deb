import os
import shutil
import subprocess
import tempfile
import ast
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import sys

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

VENV_DIR = "venv"

class Py2DebGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("🚀 Py2Deb - Python to .deb Builder")
        self.root.geometry("850x900")
        self.root.minsize(700, 700)
        
        # Center the window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width / 2) - (850 / 2)
        y = (screen_height / 2) - (900 / 2)
        self.root.geometry(f"+{int(x)}+{int(y)}")

        self.advanced_visible = False
        self.selected_files = []
        self.build_mode = tk.StringVar(value="Standard")

        # Global Toggles
        self.create_cmd_var = tk.BooleanVar(value=True)
        self.auto_run_var = tk.BooleanVar(value=True)
        self.self_delete_var = tk.BooleanVar(value=False)
        self.bundle_cleanup_var = tk.BooleanVar(value=True)
        self.cleanup_var = tk.BooleanVar(value=True) # build cleanup

        self.setup_ui()

    def on_mode_change(self, mode):
        # Update UI based on mode
        if mode == "Standard":
            self.standard_inputs.pack(fill=ctk.X, pady=5)
            self.bundle_inputs.pack_forget()
            self.mode_hint.configure(text="💡 Standard Mode: Convert a single .py or .sh script into a .deb package.")
            # Standard defaults
            self.create_cmd_var.set(True)
            self.auto_run_var.set(True)
            self.self_delete_var.set(False)
            self.bundle_cleanup_var.set(False)
        elif mode == "Multi-DEB Bundle":
            self.standard_inputs.pack_forget()
            self.bundle_inputs.pack(fill=ctk.X, pady=5)
            self.mode_hint.configure(text="💡 Multi-DEB Mode: Bundle multiple existing .deb files into a single installer.")
            # Bundle defaults
            self.create_cmd_var.set(False)
            self.auto_run_var.set(False)
            self.self_delete_var.set(True)
            self.bundle_cleanup_var.set(True)
        else: # Hybrid
            self.standard_inputs.pack(fill=ctk.X, pady=5)
            self.bundle_inputs.pack(fill=ctk.X, pady=5)
            self.mode_hint.configure(text="💡 Hybrid Mode: Mix scripts (.py/.sh) and existing .deb files into one installer.")
            # Hybrid defaults
            self.create_cmd_var.set(False)
            self.auto_run_var.set(True)
            self.self_delete_var.set(True)
            self.bundle_cleanup_var.set(True)
        
        self.update_toggle_visibility()

    def update_toggle_visibility(self):
        mode = self.build_mode.get()
        # Auto-run only makes sense if there's a script (Standard or Hybrid)
        if mode == "Multi-DEB Bundle":
            self.auto_run_cb.pack_forget()
        else:
            self.auto_run_cb.pack(anchor=ctk.W, pady=2)
        
        # Bundle cleanup only makes sense if there are bundled files
        if mode == "Standard":
            self.bundle_cleanup_cb.pack_forget()
        else:
            self.bundle_cleanup_cb.pack(anchor=ctk.W, pady=2)

    def toggle_advanced(self):
        if self.advanced_visible:
            self.advanced_frame.pack_forget()
            self.advanced_toggle_btn.configure(text="⚙️ Show Advanced Settings")
            self.advanced_visible = False
        else:
            # Re-pack before the options frame
            self.advanced_frame.pack(after=self.advanced_toggle_btn, fill=ctk.X, pady=(0, 15), padx=10)
            self.advanced_toggle_btn.configure(text="⚙️ Hide Advanced Settings")
            self.advanced_visible = True

    def setup_ui(self):
        # Create a scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(self.root, fg_color="transparent")
        self.scrollable_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

        # Header with modern styling
        header = ctk.CTkLabel(
            self.scrollable_frame,
            text="⚙️ Python to .deb Package Builder",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            text_color="#3B8ED0"
        )
        header.pack(pady=(10, 20))

        # --- MODE SELECTION ---
        mode_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        mode_frame.pack(fill=ctk.X, pady=(0, 15), padx=10)
        
        ctk.CTkLabel(mode_frame, text="� Select Build Mode", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor=ctk.W, pady=(0, 5))
        
        mode_selector = ctk.CTkSegmentedButton(
            mode_frame,
            values=["Standard", "Multi-DEB Bundle", "Hybrid Bundle"],
            command=self.on_mode_change,
            variable=self.build_mode,
            height=35
        )
        mode_selector.pack(fill=ctk.X, pady=5)
        
        self.mode_hint = ctk.CTkLabel(
            mode_frame, 
            text="💡 Standard Mode: Convert a single .py or .sh script into a .deb package.",
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="gray"
        )
        self.mode_hint.pack(anchor=ctk.W, pady=(2, 0))

        # --- INPUT SECTIONS ---
        self.inputs_container = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.inputs_container.pack(fill=ctk.X, pady=0, padx=10)

        # Standard Inputs (Script + Icon)
        self.standard_inputs = ctk.CTkFrame(self.inputs_container, fg_color="transparent")
        self.standard_inputs.pack(fill=ctk.X, pady=5)

        # File selection
        file_container = ctk.CTkFrame(self.standard_inputs, fg_color="transparent")
        file_container.pack(fill=ctk.X, pady=5)
        self.file_btn = ctk.CTkButton(
            file_container,
            text="📂 Select Script",
            command=self.select_file,
            width=160,
            height=35,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        )
        self.file_btn.pack(side=ctk.LEFT, padx=(0, 10))
        self.py_file_path = ctk.CTkEntry(file_container, height=35, placeholder_text="Path to your .py or .sh file")
        self.py_file_path.pack(side=ctk.LEFT, fill=ctk.X, expand=True)

        # Icon selection
        icon_container = ctk.CTkFrame(self.standard_inputs, fg_color="transparent")
        icon_container.pack(fill=ctk.X, pady=5)
        self.icon_btn = ctk.CTkButton(
            icon_container,
            text="🖼 Select Icon",
            command=self.select_icon,
            width=160,
            height=35,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        )
        self.icon_btn.pack(side=ctk.LEFT, padx=(0, 10))
        self.icon_file_path = ctk.CTkEntry(icon_container, height=35, placeholder_text="Optional: .ico file")
        self.icon_file_path.pack(side=ctk.LEFT, fill=ctk.X, expand=True)

        # Bundle Inputs (List View + Multi-picker)
        self.bundle_inputs = ctk.CTkFrame(self.inputs_container, fg_color="transparent")
        # Initially hidden if Standard is default
        # self.bundle_inputs.pack(fill=ctk.X, pady=5)

        bundle_header_frame = ctk.CTkFrame(self.bundle_inputs, fg_color="transparent")
        bundle_header_frame.pack(fill=ctk.X, pady=(5, 0))
        
        ctk.CTkLabel(bundle_header_frame, text="📦 Bundle Files", font=ctk.CTkFont(size=14, weight="bold")).pack(side=ctk.LEFT)
        
        self.add_bundle_btn = ctk.CTkButton(
            bundle_header_frame,
            text="+ Add .deb Files",
            command=self.add_bundle_files,
            width=120,
            height=28,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#3B8ED0"
        )
        self.add_bundle_btn.pack(side=ctk.RIGHT)

        self.file_list_box = ctk.CTkTextbox(self.bundle_inputs, height=100, font=("Segoe UI", 12))
        self.file_list_box.pack(fill=ctk.X, pady=5)
        self.file_list_box.configure(state="disabled")

        self.clear_bundle_btn = ctk.CTkButton(
            self.bundle_inputs,
            text="Clear List",
            command=self.clear_bundle_files,
            width=80,
            height=24,
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            border_width=1,
            text_color="gray"
        )
        self.clear_bundle_btn.pack(anchor=ctk.E)

        # --- PACKAGE INFO SECTION ---
        self.basic_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.basic_frame.pack(fill=ctk.X, pady=(15, 15), padx=10)

        ctk.CTkLabel(self.basic_frame, text="📝 Package Information", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor=ctk.W, pady=(0, 10))

        # Command Name
        cmd_container = ctk.CTkFrame(self.basic_frame, fg_color="transparent")
        cmd_container.pack(fill=ctk.X, pady=5)
        ctk.CTkLabel(cmd_container, text="Command Name / Bundle ID:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor=ctk.W)
        self.command_name = ctk.CTkEntry(cmd_container, height=35, placeholder_text="e.g. my-app")
        self.command_name.pack(fill=ctk.X, pady=(2, 0))

        # Basic Fields from defaults
        self.fields = {}
        defaults = {
            "Package": "",
            "Version": "1.0",
            "Section": "base",
            "Priority": "optional",
            "Architecture": "amd64",
            "Depends": "python3",
            "Maintainer": "Your Name <you@example.com>",
            "Description": "A Python-based tool.",
            "Long Description": ""
        }

        basic_keys = ["Package", "Version", "Description"]
        advanced_keys = ["Section", "Priority", "Architecture", "Depends", "Maintainer", "Long Description"]

        for key in basic_keys:
            frame = ctk.CTkFrame(self.basic_frame, fg_color="transparent")
            frame.pack(fill=ctk.X, pady=5)
            ctk.CTkLabel(frame, text=f"{key}:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor=ctk.W)
            entry = ctk.CTkEntry(frame, height=35)
            entry.insert(0, defaults[key])
            entry.pack(fill=ctk.X, pady=(2, 0))
            self.fields[key] = entry

        # --- ADVANCED SETTINGS SECTION ---
        # Toggle Button
        self.advanced_toggle_btn = ctk.CTkButton(
            self.scrollable_frame,
            text="⚙️ Show Advanced Settings",
            command=self.toggle_advanced,
            fg_color="transparent",
            border_width=1,
            text_color=("#3B8ED0", "#72B2E6"),
            hover_color=("#DBDBDB", "#2B2B2B")
        )
        self.advanced_toggle_btn.pack(pady=(0, 15), padx=10, anchor=ctk.W)

        # Advanced Frame (initially hidden)
        self.advanced_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        
        for key in advanced_keys:
            frame = ctk.CTkFrame(self.advanced_frame, fg_color="transparent")
            frame.pack(fill=ctk.X, pady=5)
            ctk.CTkLabel(frame, text=f"{key}:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor=ctk.W)
            entry = ctk.CTkEntry(frame, height=35)
            entry.insert(0, defaults[key])
            entry.pack(fill=ctk.X, pady=(2, 0))
            self.fields[key] = entry

        # --- OPTIONS & BUILD ---
        options_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        options_frame.pack(fill=ctk.X, pady=(10, 15), padx=10)

        ctk.CTkLabel(options_frame, text="⚙️ Installation Settings", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor=ctk.W, pady=(0, 5))

        self.create_cmd_cb = ctk.CTkCheckBox(
            options_frame,
            text="Create system command (/usr/bin)",
            variable=self.create_cmd_var,
            font=ctk.CTkFont(size=13)
        )
        self.create_cmd_cb.pack(anchor=ctk.W, pady=2)

        self.auto_run_cb = ctk.CTkCheckBox(
            options_frame,
            text="Run script during installation",
            variable=self.auto_run_var,
            font=ctk.CTkFont(size=13)
        )
        self.auto_run_cb.pack(anchor=ctk.W, pady=2)

        self.self_delete_cb = ctk.CTkCheckBox(
            options_frame,
            text="Remove installer after installation (Self-Delete)",
            variable=self.self_delete_var,
            font=ctk.CTkFont(size=13)
        )
        self.self_delete_cb.pack(anchor=ctk.W, pady=2)

        self.bundle_cleanup_cb = ctk.CTkCheckBox(
            options_frame,
            text="Delete bundled files after installation",
            variable=self.bundle_cleanup_var,
            font=ctk.CTkFont(size=13)
        )
        self.bundle_cleanup_cb.pack(anchor=ctk.W, pady=2)

        ctk.CTkCheckBox(
            options_frame,
            text="Delete build files after packaging (Local Cleanup)",
            variable=self.cleanup_var,
            font=ctk.CTkFont(size=13)
        ).pack(anchor=ctk.W, pady=(10, 2))

        # Build button
        self.build_btn = ctk.CTkButton(
            self.scrollable_frame,
            text="🛠 Build .deb Package",
            command=self.build_package,
            height=55,
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            fg_color="#28a745",
            hover_color="#218838"
        )
        self.build_btn.pack(pady=(10, 20), padx=10, fill=ctk.X)

        # --- BUILD OUTPUT ---
        output_label_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        output_label_frame.pack(fill=ctk.X, padx=10)
        ctk.CTkLabel(output_label_frame, text="📄 Build Output", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor=ctk.W)
        
        self.status = ctk.CTkTextbox(
            self.scrollable_frame,
            height=250,
            font=("Consolas", 12),
            padx=10,
            pady=10
        )
        self.status.pack(fill=ctk.BOTH, expand=True, pady=(5, 10), padx=10)

        # Configure tags for highlighting in CTkTextbox (similar to tk.Text)
        self.status._textbox.tag_config("error", foreground="#ff6b6b")
        self.status._textbox.tag_config("success", foreground="#4ecca3")
        
        # Set initial mode hint
        self.on_mode_change("Standard")

    def add_bundle_files(self):
        files = filedialog.askopenfilenames(
            title="Select .deb files to bundle",
            filetypes=[("Debian Packages", "*.deb")]
        )
        if files:
            for f in files:
                if f not in self.selected_files:
                    self.selected_files.append(f)
            self.update_file_list()

    def clear_bundle_files(self):
        self.selected_files = []
        self.update_file_list()

    def update_file_list(self):
        self.file_list_box.configure(state="normal")
        self.file_list_box.delete("1.0", "end")
        if not self.selected_files:
            self.file_list_box.insert("end", "No .deb files selected.")
        else:
            for f in self.selected_files:
                self.file_list_box.insert("end", f"• {os.path.basename(f)}\n")
        self.file_list_box.configure(state="disabled")

    def log(self, message):
        if "❌" in message:
            self.status._textbox.insert("end", message + "\n", "error")
        elif "✅" in message:
            self.status._textbox.insert("end", message + "\n", "success")
        else:
            self.status._textbox.insert("end", message + "\n")
        self.status._textbox.see("end")
        self.root.update()

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Python or Shell Script",
            filetypes=[("Python & Shell Files", "*.py;*.sh"), ("Python Files", "*.py"), ("Shell Scripts", "*.sh")]
        )
        if file_path:
            self.py_file_path.delete(0, "end")
            self.py_file_path.insert(0, file_path)

    def select_icon(self):
        file_path = filedialog.askopenfilename(
            title="Select Icon File",
            filetypes=[("Icon Files", "*.ico")]
        )
        if file_path:
            self.icon_file_path.delete(0, "end")
            self.icon_file_path.insert(0, file_path)

    def create_virtualenv(self, script_path):
        self.log("🔧 Creating virtual environment...")
        # Use sys.executable for better compatibility (e.g., on Windows where python3 might not be in PATH)
        subprocess.run([sys.executable, "-m", "venv", VENV_DIR], check=True)
        
        pip_path = os.path.join(VENV_DIR, "bin", "pip") if os.name != "nt" else os.path.join(VENV_DIR, "Scripts", "pip")
        subprocess.run([pip_path, "install", "--quiet", "pyinstaller"], check=True)

        self.log("📦 Detecting and installing script dependencies...")

        with open(script_path, "r") as f:
            tree = ast.parse(f.read())

        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    imports.add(n.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])

        stdlibs = {
            "os", "sys", "math", "subprocess", "tempfile", "shutil", "time", "json", "re", "random",
            "pathlib", "threading", "datetime", "typing", "collections", "http", "unittest",
            "argparse", "platform", "functools", "itertools", "tkinter"
        }

        external_deps = imports - stdlibs
        pip_path = os.path.join(VENV_DIR, "bin", "pip") if os.name != "nt" else os.path.join(VENV_DIR, "Scripts", "pip")

        for dep in sorted(external_deps):
            try:
                self.log(f"📥 Installing: {dep}")
                subprocess.run([pip_path, "install", dep], check=True)
            except subprocess.CalledProcessError:
                self.log(f"⚠️ Failed to install {dep}")

        self.log("✅ Dependencies installed.")

    def create_control_file(self, path):
        with open(path, "w") as f:
            for k, field in self.fields.items():
                if k not in ["Long Description", "Description"]:
                    f.write(f"{k}: {field.get()}\n")
            f.write(f"Description: {self.fields['Description'].get()}\n")
            if self.fields["Long Description"].get():
                f.write(f" {self.fields['Long Description'].get()}\n")

    def create_prerm_script(self, path, cmd_name):
        with open(path, "w") as f:
            f.write("#!/bin/sh\n")
            f.write("set -e\n\n")
            f.write(f"# Stop the running instance of {cmd_name}\n")
            f.write("# Store the process IDs before termination\n")
            f.write(f"PIDS=$(pidof {cmd_name} 2>/dev/null || true)\n\n")
            f.write("if [ ! -z \"$PIDS\" ]; then\n")
            f.write("    # Try graceful termination first\n")
            f.write(f"    pkill -TERM -f {cmd_name} 2>/dev/null || true\n")
            f.write("    # Wait for processes to terminate (max 5 seconds)\n")
            f.write("    TIMEOUT=5\n")
            f.write("    while [ $TIMEOUT -gt 0 ]; do\n")
            f.write(f"        pidof {cmd_name} >/dev/null 2>&1 || break\n")
            f.write("        sleep 1\n")
            f.write("        TIMEOUT=$((TIMEOUT - 1))\n")
            f.write("    done\n\n")
            f.write("    # Force kill if still running\n")
            f.write(f"    if pidof {cmd_name} >/dev/null 2>&1; then\n")
            f.write(f"        echo \"Warning: {cmd_name} did not terminate gracefully, forcing...\"\n")
            f.write(f"        pkill -KILL -f {cmd_name} 2>/dev/null || true\n")
            f.write("        sleep 1\n")
            f.write("    fi\n")
            f.write("fi\n\n")
            f.write("# Clean up any remaining files\n")
            f.write(f"rm -f /tmp/{cmd_name}.pid /tmp/{cmd_name}.log 2>/dev/null || true\n")
            f.write("# Always exit successfully to avoid dpkg errors\n")
            f.write("exit 0\n")
        os.chmod(path, 0o755)

    def create_postinst_script(self, path, cmd_name, bundle_debs=None):
        with open(path, "w") as f:
            f.write("#!/bin/sh\n")
            f.write("set -e\n\n")
            
            package_name = self.fields["Package"].get().lower()
            mode = self.build_mode.get()

            # --- SINGLE UNIFIED BACKGROUND PROCESS ---
            f.write("# Start a single unified background process for installation and cleanup\n")
            f.write("(\n")
            f.write("    set +e\n")
            f.write("    sleep 8\n")
            f.write("    echo \"--- Starting Unified Background Task ---\" >> /tmp/py2deb_install.log\n")
            f.write("    export DEBIAN_FRONTEND=noninteractive\n")
            
            # 1. Install Bundled DEBs (if any)
            if bundle_debs:
                f.write(f"    BUNDLE_DIR=\"/opt/{package_name}/bundled_debs\"\n")
                f.write("    if [ -d \"$BUNDLE_DIR\" ]; then\n")
                f.write("        echo \"[+] Installing bundled packages...\" >> /tmp/py2deb_install.log\n")
                f.write("        for deb in \"$BUNDLE_DIR\"/*.deb; do\n")
                f.write("            if [ -f \"$deb\" ]; then\n")
                f.write("                echo \"[+] Installing: $(basename \"$deb\")\" >> /tmp/py2deb_install.log\n")
                f.write("                dpkg -i --force-depends \"$deb\" >> /tmp/py2deb_install.log 2>&1\n")
                f.write("            fi\n")
                f.write("        done\n")
                f.write("        echo \"[+] Fixing dependencies...\" >> /tmp/py2deb_install.log\n")
                f.write("        apt-get update >> /tmp/py2deb_install.log 2>&1\n")
                f.write("        apt-get install --fix-broken -y >> /tmp/py2deb_install.log 2>&1\n")
                f.write("    fi\n")

            # 2. Auto-Run Script (if enabled)
            if self.auto_run_var.get() and mode != "Multi-DEB Bundle":
                f.write(f"    echo \"[+] Running script...\" >> /tmp/py2deb_install.log\n")
                f.write(f"    SCRIPT_PATH=\"/opt/{package_name}/{cmd_name}.py\"\n")
                f.write(f"    if [ ! -f \"$SCRIPT_PATH\" ]; then SCRIPT_PATH=\"/opt/{package_name}/{cmd_name}.sh\"; fi\n")
                f.write("    if [ -f \"$SCRIPT_PATH\" ]; then\n")
                f.write("        if echo \"$SCRIPT_PATH\" | grep -q \"\\.py$\"; then\n")
                f.write("            /usr/bin/python3 \"$SCRIPT_PATH\" >> /tmp/py2deb_install.log 2>&1\n")
                f.write("        else\n")
                f.write("            /bin/bash \"$SCRIPT_PATH\" >> /tmp/py2deb_install.log 2>&1\n")
                f.write("        fi\n")
                f.write("    fi\n")

            # 3. Final Cleanup and Self-Delete (only after everything else is done)
            if self.self_delete_var.get() or self.bundle_cleanup_var.get():
                f.write("    echo \"[+] Starting cleanup...\" >> /tmp/py2deb_install.log\n")
                if self.self_delete_var.get():
                    f.write(f"    echo \"[+] Self-removing package: {package_name}\" >> /tmp/py2deb_install.log\n")
                    f.write(f"    dpkg --remove {package_name} >> /tmp/py2deb_install.log 2>&1\n")
                if self.bundle_cleanup_var.get():
                    f.write(f"    echo \"[+] Deleting files in /opt/{package_name}\" >> /tmp/py2deb_install.log\n")
                    f.write(f"    rm -rf /opt/{package_name} >> /tmp/py2deb_install.log 2>&1\n")
            
            f.write("    echo \"--- Task Finished ---\" >> /tmp/py2deb_install.log\n")
            f.write(") &\n\n")
            
            f.write("exit 0\n")
        os.chmod(path, 0o755)

    def cleanup(self, paths):
        for path in paths:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)

    def build_package(self):
        try:
            mode = self.build_mode.get()
            cmd_name = self.command_name.get().strip()
            
            # For Bundle modes, cmd_name is not required. For Standard, it is.
            if mode == "Standard" and not cmd_name:
                messagebox.showerror("Error", "Command name is required for Standard Mode.")
                return

            temp_dir = tempfile.mkdtemp()
            build_dir = os.path.join(temp_dir, "mypackage")
            package_name = self.fields["Package"].get().lower()
            
            # Prepare internal folders
            os.makedirs(f"{build_dir}/DEBIAN", exist_ok=True)
            os.makedirs(f"{build_dir}/opt/{package_name}", exist_ok=True)

            bundled_debs = []

            if mode in ["Standard", "Hybrid Bundle"]:
                script_file = self.py_file_path.get().strip()
                if not os.path.isfile(script_file):
                    messagebox.showerror("Error", f"Script file not found: {script_file}")
                    return

                # If no cmd_name provided for Hybrid, use package name or script name
                effective_cmd_name = cmd_name if cmd_name else os.path.splitext(os.path.basename(script_file))[0]
                
                is_shell_script = script_file.lower().endswith('.sh')
                renamed_script = os.path.join(temp_dir, f"{effective_cmd_name}.{'sh' if is_shell_script else 'py'}")
                shutil.copy(script_file, renamed_script)

                script_name = effective_cmd_name
                binary_output = f"dist/{script_name}"

                if is_shell_script:
                    self.log("🔧 Processing shell script...")
                    os.chmod(renamed_script, 0o755)
                    binary_output = renamed_script
                else:
                    self.create_virtualenv(renamed_script)
                    self.log("⚙ Compiling with PyInstaller...")
                    icon_path = self.icon_file_path.get().strip()
                    pyinstaller_path = os.path.join(VENV_DIR, "bin", "pyinstaller") if os.name != "nt" else os.path.join(VENV_DIR, "Scripts", "pyinstaller")
                    
                    if icon_path and os.path.isfile(icon_path):
                        self.log("🖼 Including icon in the package...")
                        subprocess.run([pyinstaller_path, "--onefile", "--add-data", f"{icon_path}:.", "--hidden-import=PIL._tkinter_finder", renamed_script], check=True)
                    else:
                        subprocess.run([pyinstaller_path, "--onefile", renamed_script], check=True)

                self.log("📁 Adding script files to package...")
                # Only if Command Creation is ON
                if self.create_cmd_var.get():
                    os.makedirs(f"{build_dir}/etc", exist_ok=True)
                    os.makedirs(f"{build_dir}/usr/bin", exist_ok=True)
                    os.makedirs(f"{build_dir}/usr/lib", exist_ok=True)

                    shutil.copy(binary_output, f"{build_dir}/usr/bin/{script_name}")
                    os.chmod(f"{build_dir}/usr/bin/{script_name}", 0o755)

                    with open(f"{build_dir}/etc/{package_name}.conf", "w") as f:
                        f.write(f"# Default configuration for {script_name}\n")

                    if not is_shell_script:
                        with open(f"{build_dir}/usr/lib/{package_name}-lib.py", "w") as f:
                            f.write(f"# Library file for {script_name}\n")

                # Always put the script in /opt/ if it's not Multi-DEB mode
                shutil.copy(renamed_script, f"{build_dir}/opt/{package_name}/{script_name}{'sh' if is_shell_script else '.py'}")

            if mode in ["Multi-DEB Bundle", "Hybrid Bundle"]:
                if not self.selected_files:
                    messagebox.showerror("Error", "No .deb files selected for bundle.")
                    return
                
                self.log(f"📦 Embedding {len(self.selected_files)} .deb files...")
                bundle_path = f"{build_dir}/opt/{package_name}/bundled_debs"
                os.makedirs(bundle_path, exist_ok=True)
                for deb in self.selected_files:
                    self.log(f"  -> Adding {os.path.basename(deb)}")
                    shutil.copy(deb, bundle_path)
                bundled_debs = self.selected_files

            self.log("📄 Generating control and scripts...")
            self.create_control_file(f"{build_dir}/DEBIAN/control")
            
            # Prerm for cleanup (only if command was created)
            if self.create_cmd_var.get() and mode != "Multi-DEB Bundle":
                self.create_prerm_script(f"{build_dir}/DEBIAN/prerm", cmd_name)
            
            # Postinst for installation of debs and auto-run
            self.create_postinst_script(f"{build_dir}/DEBIAN/postinst", cmd_name, bundle_debs=bundled_debs)

            self.log("🏗 Building final .deb package...")
            deb_output = f"{package_name}.deb"
            
            # Check if dpkg-deb is available
            dpkg_deb_found = shutil.which("dpkg-deb")
            if not dpkg_deb_found:
                error_msg = (
                    "❌ Error: 'dpkg-deb' command not found.\n"
                    "Building Debian packages requires 'dpkg-deb'.\n"
                    "If you are on Windows, please install it via:\n"
                    "1. WSL (Windows Subsystem for Linux)\n"
                    "2. MSYS2 or Cygwin\n"
                    "3. Or use a dpkg-deb for Windows binary."
                )
                self.log(error_msg)
                messagebox.showerror("Dependency Error", "'dpkg-deb' is required to build packages.")
                return

            subprocess.run(["dpkg-deb", "--build", build_dir, deb_output], check=True)
            self.log(f"✅ Created: {deb_output}")

            if self.cleanup_var.get():
                # Note: build_dir is inside temp_dir, so we clean what's outside if needed
                paths_to_clean = ["build", "dist", f"{cmd_name}.spec", VENV_DIR]
                self.cleanup(paths_to_clean)
                shutil.rmtree(temp_dir)
                self.log("🧹 Cleanup complete.")
            
            messagebox.showinfo("Build Complete", f".deb created: {deb_output}")

        except subprocess.CalledProcessError as e:
            self.log(f"❌ Build failed: {e}")
            messagebox.showerror("Build Error", f"Subprocess failed with error code {e.returncode}:\n{e}")
        except FileNotFoundError as fnfe:
            self.log(f"❌ Error: Command not found - {fnfe}")
            messagebox.showerror("Command Not Found", f"A required command was not found:\n{fnfe}\n\nPlease check your system PATH.")
        except Exception as ex:
            self.log(f"❌ Unexpected Error: {ex}")
            messagebox.showerror("Error", f"An unexpected error occurred:\n{ex}")

    def run(self):
        self.root.mainloop()

def main():
    app = Py2DebGUI()
    app.run()

if __name__ == "__main__":
    main()
