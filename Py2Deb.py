import os
import shutil
import subprocess
import tempfile
import ast
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import sys

VENV_DIR = "venv"

class Py2DebGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚀 Py2Deb - Python to .deb Builder")
        self.root.geometry("700x600")
        self.root.minsize(500, 400)
        self.root.eval('tk::PlaceWindow . center')
        self.root.configure(bg="#f0f0f0")
        self.root.option_add("*TCombobox*Listbox.background", "#2a2a40")
        self.root.option_add("*TCombobox*Listbox.foreground", "#ffffff")
        self.root.option_add("*TButton*background", "#2196F3")
        self.root.option_add("*TButton*foreground", "#ffffff")
        self.root.option_add("*TButton*font", ("Segoe UI", 10, "bold"))
        self.root.option_add("*TButton*relief", "raised")
        self.root.option_add("*TCheckbutton*background", "#1a1a2e")
        self.root.option_add("*TCheckbutton*foreground", "#ffffff")
        self.root.option_add("*TCheckbutton*font", ("Segoe UI", 10))
        
        # Create style instance
        self.style = ttk.Style()
        self.setup_ui()

        # Bind window resize event
        self.root.bind("<Configure>", self.on_window_resize)

    def setup_ui(self):
        # Create a canvas with scrollbar
        self.canvas = tk.Canvas(self.root, bg="#ffffff", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        scrollable_frame = ttk.Frame(self.canvas)

        # Enable mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Configure style for accent buttons
        self.style.configure(
            "Accent.TButton",
            background="#ffffff",
            foreground="#2196F3",
            padding=10,
            font=("Segoe UI", 10, "bold"),
            relief="raised",
            borderwidth=2
        )
        
        # Map states for hover effect
        self.style.map(
            "Accent.TButton",
            background=[("active", "#1976D2")],
            relief=[("pressed", "sunken")]
        )

        # Configure style for switch checkbuttons
        self.style.configure(
            "Switch.TCheckbutton",
            background="#1a1a2e",
            foreground="#ffffff",
            font=("Segoe UI", 10)
        )

        self.style.configure("TLabel", font=("Segoe UI", 10), foreground="#333333", background="#ffffff")
        self.style.configure("TEntry", padding=5, fieldbackground="#ffffff", foreground="#333333")
        self.style.configure("TFrame", background="#ffffff")
        self.style.configure("TCheckbutton", background="#ffffff", foreground="#333333")

        # Configure root window
        self.root.configure(bg="#ffffff")
        self.root.option_add("*TCombobox*Listbox.background", "#ffffff")
        self.root.option_add("*TCombobox*Listbox.foreground", "#333333")

        # Main container
        main_frame = ttk.Frame(scrollable_frame, padding="20 20 20 20", style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header with improved styling
        header = ttk.Label(
            main_frame,
            text="⚙️ Python to .deb Package Builder",
            font=("Segoe UI", 24, "bold"),
            foreground="#2196F3",
            background="#ffffff"
        )
        header.pack(pady=(0, 20))

        # File selection frame with better spacing
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=(0, 15))

        self.file_btn = ttk.Button(
            file_frame,
            text="📂 Select Python File",
            command=self.select_file,
            style="Accent.TButton"
        )
        self.file_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.file_btn.configure(style="Accent.TButton")

        self.py_file_path = ttk.Entry(file_frame)
        self.py_file_path.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Icon selection frame
        icon_frame = ttk.Frame(main_frame)
        icon_frame.pack(fill=tk.X, pady=(0, 15))

        self.icon_btn = ttk.Button(
            icon_frame,
            text="🖼 Select Icon File",
            command=self.select_icon,
            style="Accent.TButton"
        )
        self.icon_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.icon_file_path = ttk.Entry(icon_frame)
        self.icon_file_path.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Form frame with improved spacing
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.X, pady=(0, 15))

        # Command Name with better styling
        cmd_frame = ttk.Frame(form_frame)
        cmd_frame.pack(fill=tk.X, pady=5)
        ttk.Label(cmd_frame, text="Command Name:").pack(anchor=tk.W)
        self.command_name = ttk.Entry(cmd_frame)
        self.command_name.pack(fill=tk.X, pady=(5, 0))

        # Fields with consistent spacing
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

        for label, default in defaults.items():
            frame = ttk.Frame(form_frame)
            frame.pack(fill=tk.X, pady=5)
            ttk.Label(frame, text=f"{label}:").pack(anchor=tk.W)
            entry = ttk.Entry(frame)
            entry.insert(0, default)
            entry.pack(fill=tk.X, pady=(5, 0))
            self.fields[label] = entry

        # Options frame with better alignment
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.X, pady=(10, 15))

        self.autostart_var = tk.BooleanVar(value=True)
        self.run_on_install_var = tk.BooleanVar(value=True)
        self.cleanup_var = tk.BooleanVar(value=True)

        # Only show cleanup option
        ttk.Checkbutton(
            options_frame,
            text="Delete build files after packaging",
            variable=self.cleanup_var,
            style="Switch.TCheckbutton"
        ).pack(anchor=tk.W, pady=2)

        # Build button with accent styling
        self.build_btn = ttk.Button(
            main_frame,
            text="🛠 Build .deb Package",
            command=self.build_package,
            style="Accent.TButton"
        )
        self.build_btn.pack(pady=(5, 15))

        # Status output with improved styling
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(output_frame, text="📄 Build Output:").pack(anchor=tk.W)
        
        self.status = scrolledtext.ScrolledText(
            output_frame,
            height=10,
            font=("Consolas", 10),
            bg="#ffffff",
            fg="#000000",
            insertbackground="#000000",
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.status.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # Configure tags for highlighting
        self.status.tag_configure("error", foreground="#ff6b6b")
        self.status.tag_configure("success", foreground="#4ecca3")

        # Pack canvas and scrollbar
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure style for accent buttons
        self.style.configure(
            "Accent.TButton",
            background="#ffffff",
            foreground="#2196F3",
            padding=10,
            font=("Segoe UI", 10, "bold"),
            relief="raised",
            borderwidth=2
        )
        
        # Map states for hover effect
        self.style.map(
            "Accent.TButton",
            background=[("active", "#1976D2")],
            relief=[("pressed", "sunken")]
        )

        # Configure style for accent buttons
        self.style.configure(
            "Accent.TButton",
            background="#ffffff",
            foreground="#2196F3",
            padding=10,
            font=("Segoe UI", 10, "bold"),
            relief="raised",
            borderwidth=2
        )
        
        # Map states for hover effect
        self.style.map(
            "Accent.TButton",
            background=[("active", "#1976D2")],
            relief=[("pressed", "sunken")]
        )

        # Configure style for accent buttons
        self.style.configure(
            "Accent.TButton",
            background="#ffffff",
            foreground="#2196F3",
            padding=10,
            font=("Segoe UI", 10, "bold"),
            relief="raised",
            borderwidth=2
        )
        
        # Map states for hover effect
        self.style.map(
            "Accent.TButton",
            background=[("active", "#1976D2")],
            relief=[("pressed", "sunken")]
        )

        # Configure style for switch checkbuttons
        self.style.configure(
            "Switch.TCheckbutton",
            background="#1a1a2e",
            foreground="#ffffff",
            font=("Segoe UI", 10)
        )

    def on_window_resize(self, event):
        # Update the canvas scrollregion when the window is resized
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def log(self, message):
        if "❌" in message:
            self.status.insert(tk.END, message + "\n", "error")
        elif "✅" in message:
            self.status.insert(tk.END, message + "\n", "success")
        else:
            self.status.insert(tk.END, message + "\n")
        self.status.see(tk.END)
        self.root.update()

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Python or Shell Script",
            filetypes=[("Python & Shell Files", "*.py;*.sh"), ("Python Files", "*.py"), ("Shell Scripts", "*.sh")]
        )
        if file_path:
            self.py_file_path.delete(0, tk.END)
            self.py_file_path.insert(0, file_path)

    def select_icon(self):
        file_path = filedialog.askopenfilename(
            title="Select Icon File",
            filetypes=[("Icon Files", "*.ico")]
        )
        if file_path:
            self.icon_file_path.delete(0, tk.END)
            self.icon_file_path.insert(0, file_path)

    def create_virtualenv(self, script_path):
        self.log("🔧 Creating virtual environment...")
        subprocess.run(["python3", "-m", "venv", VENV_DIR], check=True)
        subprocess.run([f"{VENV_DIR}/bin/pip", "install", "--quiet", "pyinstaller"], check=True)

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

        for dep in sorted(external_deps):
            try:
                self.log(f"📥 Installing: {dep}")
                subprocess.run([f"{VENV_DIR}/bin/pip", "install", dep], check=True)
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

    def create_postinst_script(self, path, cmd_name):
        with open(path, "w") as f:
            f.write("#!/bin/sh\n")
            f.write("set -e\n\n")
            if self.run_on_install_var.get():
                f.write(f"# Run {cmd_name} after installation\n")
                package_name = self.fields["Package"].get().lower()
                f.write(f"# Ensure binary exists and is executable\n")
                f.write(f"chmod +x /usr/bin/{cmd_name}\n\n")
                f.write(f"# Run binary in background with output logging\n")
                f.write(f"/usr/bin/{cmd_name} > /tmp/{package_name}.log 2>&1 &\n")
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
            script_file = self.py_file_path.get().strip()
            cmd_name = self.command_name.get().strip()

            if not os.path.isfile(script_file):
                messagebox.showerror("Error", "Script file not found.")
                return
            if not cmd_name:
                messagebox.showerror("Error", "Command name cannot be empty.")
                return

            temp_dir = tempfile.mkdtemp()
            is_shell_script = script_file.lower().endswith('.sh')
            renamed_script = os.path.join(temp_dir, f"{cmd_name}.{'sh' if is_shell_script else 'py'}")
            shutil.copy(script_file, renamed_script)

            script_name = cmd_name
            build_dir = "mypackage"
            binary_output = f"dist/{script_name}"

            if is_shell_script:
                self.log("🔧 Processing shell script...")
                # Make the shell script executable
                os.chmod(renamed_script, 0o755)
                # Copy the shell script as the binary
                binary_output = renamed_script
            else:
                self.create_virtualenv(renamed_script)
                self.log("⚙ Compiling with PyInstaller...")
                icon_path = self.icon_file_path.get().strip()
                if icon_path and os.path.isfile(icon_path):
                    self.log("🖼 Including icon in the package...")
                    subprocess.run([f"{VENV_DIR}/bin/pyinstaller", "--onefile", "--add-data", f"{icon_path}:.", "--hidden-import=PIL._tkinter_finder", renamed_script], check=True)
                else:
                    subprocess.run([f"{VENV_DIR}/bin/pyinstaller", "--onefile", renamed_script], check=True)

            self.log("📁 Creating folder structure...")
            package_name = self.fields["Package"].get().lower()
            os.makedirs(f"{build_dir}/DEBIAN", exist_ok=True)
            os.makedirs(f"{build_dir}/etc", exist_ok=True)
            os.makedirs(f"{build_dir}/opt/{package_name}", exist_ok=True)
            os.makedirs(f"{build_dir}/usr/bin", exist_ok=True)
            os.makedirs(f"{build_dir}/usr/lib", exist_ok=True)

            # Copy binary to usr/bin
            shutil.copy(binary_output, f"{build_dir}/usr/bin/{script_name}")
            os.chmod(f"{build_dir}/usr/bin/{script_name}", 0o755)

            # Create configuration file
            with open(f"{build_dir}/etc/{package_name}.conf", "w") as f:
                f.write(f"# Default configuration for {script_name}\n")
                f.write("# Modify this file according to your needs\n")

            # Copy original script
            shutil.copy(renamed_script, f"{build_dir}/opt/{package_name}/{script_name}{'sh' if is_shell_script else '.py'}")
            
            # Create library file only for Python scripts
            if not is_shell_script:
                with open(f"{build_dir}/usr/lib/{package_name}-lib.py", "w") as f:
                    f.write(f"# Library file for {script_name}\n")
                    f.write("# Add your library functions here\n")

            self.create_control_file(f"{build_dir}/DEBIAN/control")
            self.create_prerm_script(f"{build_dir}/DEBIAN/prerm", script_name)
            self.create_postinst_script(f"{build_dir}/DEBIAN/postinst", script_name)

            self.log("📦 Building .deb package...")
            package_name = self.fields["Package"].get().lower()
            deb_output = f"{package_name}.deb"
            subprocess.run(["dpkg-deb", "--build", build_dir, deb_output], check=True)
            self.log(f"✅ Created: {deb_output}")

            if self.cleanup_var.get():
                self.cleanup([
                    build_dir,
                    "build",
                    "dist",
                    f"{script_name}.spec",
                    VENV_DIR,
                    temp_dir
                ])
                self.log("🧹 Cleanup complete. .deb is ready.")
            else:
                self.log("📝 Build files preserved as requested.")

            messagebox.showinfo("Build Complete", f".deb created: {deb_output}")

        except subprocess.CalledProcessError as e:
            self.log(f"❌ Build failed: {e}")
            messagebox.showerror("Build Error", str(e))
        except Exception as ex:
            self.log(f"❌ Unexpected Error: {ex}")
            messagebox.showerror("Error", str(ex))

    def run(self):
        self.root.mainloop()

def main():
    app = Py2DebGUI()
    app.run()

if __name__ == "__main__":
    main()
