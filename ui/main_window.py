"""
Main Window for Claude Settings Manager
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
from pathlib import Path
import config
from manager.file_manager import FileManager
from manager.json_manager import JsonManager


class MainWindow:
    """Main application window"""

    def __init__(self, root):
        self.root = root
        self.root.title(config.WINDOW_TITLE)
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.root.minsize(config.MIN_WINDOW_WIDTH, config.MIN_WINDOW_HEIGHT)

        # Apply minimalist theme
        self._apply_theme()

        # Current selected file
        self.current_file = None
        self.original_json = ""

        # Create UI
        self._create_top_bar()
        self._create_layout()
        self._create_left_panel()
        self._create_right_panel()

        # Load initial data
        self._refresh_file_list()

        # Configure grid weights
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def _create_top_bar(self):
        """Create the top bar with global config button"""
        top_bar = ttk.Frame(self.root, padding=(10, 10, 10, 0))
        top_bar.grid(row=0, column=0, sticky="ew")

        # Global config button
        self.config_button = ttk.Button(
            top_bar,
            text="全局配置",
            command=self._on_global_config
        )
        self.config_button.pack(side=tk.RIGHT)

    def _apply_theme(self):
        """Apply minimalist color theme"""
        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')

        # Configure treeview
        style.configure("Treeview",
                       background=config.TREE_BG_COLOR,
                       foreground=config.FG_COLOR,
                       fieldbackground=config.TREE_BG_COLOR,
                       borderwidth=0,
                       relief='flat')
        style.configure("Treeview.Heading",
                       background=config.BG_COLOR,
                       foreground=config.FG_COLOR,
                       borderwidth=0,
                       relief='flat')
        style.map("Treeview",
                 background=[('selected', config.TREE_SELECT_COLOR)],
                 foreground=[('selected', config.FG_COLOR)])
        style.map("Treeview.Heading",
                 background=[('active', config.BG_COLOR)])

        # Configure frame
        style.configure("TFrame", background=config.BG_COLOR)

        # Configure label
        style.configure("TLabel",
                       background=config.BG_COLOR,
                       foreground=config.FG_COLOR)

        # Configure button
        style.configure("TButton",
                       background=config.BG_COLOR,
                       foreground=config.FG_COLOR,
                       borderwidth=1,
                       relief='flat',
                       padding=(10, 5))
        style.map("TButton",
                 background=[('active', config.TREE_SELECT_COLOR)],
                 relief=[('pressed', 'sunken'), ('active', 'raised')])

        # Configure paned window
        style.configure("TPanedwindow", background=config.BG_COLOR)

        # Apply background to root
        self.root.configure(bg=config.BG_COLOR)

    def _create_layout(self):
        """Create the main layout"""
        # Main container with paned window
        self.paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned_window.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # Left frame for file list
        self.left_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.left_frame, weight=1)

        # Right frame for editor
        self.right_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.right_frame, weight=2)

    def _create_left_panel(self):
        """Create the left panel with file list and buttons"""
        # Title label
        title_label = ttk.Label(self.left_frame, text="配置列表", font=("Microsoft YaHei UI", 10, "bold"))
        title_label.pack(anchor="w", pady=(0, 10))

        # Button frame
        button_frame = ttk.Frame(self.left_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        # Add button
        self.add_button = ttk.Button(button_frame, text="新建配置", command=self._on_add_file)
        self.add_button.pack(side=tk.LEFT, padx=(0, 10))

        # Delete button
        self.delete_button = ttk.Button(button_frame, text="删除配置", command=self._on_delete_file, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT)

        # Treeview for file list
        tree_frame = ttk.Frame(self.left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=config.TREE_COLUMNS,
            show="headings",
            yscrollcommand=scrollbar.set
        )

        # Configure columns
        self.tree.heading(config.TREE_COLUMNS[0], text=config.TREE_HEADING_FILENAME)
        self.tree.heading(config.TREE_COLUMNS[1], text=config.TREE_HEADING_ACTIVE)

        self.tree.column(config.TREE_COLUMNS[0], width=config.TREE_COLUMN_WIDTH_FILENAME)
        self.tree.column(config.TREE_COLUMNS[1], width=config.TREE_COLUMN_WIDTH_ACTIVE, anchor=tk.CENTER)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)

        # Configure tags for active items
        self.tree.tag_configure("active", background=config.TREE_SELECT_COLOR)

        # Bind events
        self.tree.bind("<<TreeviewSelect>>", self._on_file_select)
        self.tree.bind("<Button-3>", self._on_right_click)  # Right-click

    def _create_right_panel(self):
        """Create the right panel with JSON editor"""
        # Title label
        self.editor_title = ttk.Label(self.right_frame, text="JSON 编辑器", font=("Microsoft YaHei UI", 10, "bold"))
        self.editor_title.pack(anchor="w", pady=(0, 10))

        # Text widget for JSON editing
        text_frame = ttk.Frame(self.right_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.json_text = scrolledtext.ScrolledText(
            text_frame,
            font=(config.JSON_FONT_FAMILY, config.JSON_FONT_SIZE),
            wrap=tk.NONE,
            padx=10,
            pady=10,
            background=config.TREE_BG_COLOR,
            foreground=config.FG_COLOR,
            insertbackground=config.FG_COLOR,
            borderwidth=0,
            relief='flat'
        )
        self.json_text.pack(fill=tk.BOTH, expand=True)

        # Disable initially
        self.json_text.config(state=tk.DISABLED)

        # Button frame
        button_frame = ttk.Frame(self.right_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # Save button
        self.save_button = ttk.Button(button_frame, text="保存", command=self._on_save, state=tk.DISABLED)
        self.save_button.pack(side=tk.RIGHT, padx=(10, 0))

        # Format button
        self.format_button = ttk.Button(button_frame, text="格式化", command=self._on_format, state=tk.DISABLED)
        self.format_button.pack(side=tk.RIGHT, padx=(10, 0))

        # Status label
        self.status_label = ttk.Label(button_frame, text="", foreground="gray")
        self.status_label.pack(side=tk.LEFT)

    def _refresh_file_list(self):
        """Refresh the file list"""
        # Clear current list
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Get files and active settings
        files = FileManager.get_settings_files()
        active = FileManager.get_active_settings()

        # Populate tree
        for filename in files:
            active_label = config.ACTIVE_LABEL if filename == active else config.INACTIVE_LABEL
            item_id = self.tree.insert("", tk.END, values=(filename, active_label))

            # Color active item
            if filename == active:
                self.tree.item(item_id, tags=("active",))

    def _on_file_select(self, event):
        """Handle file selection"""
        selection = self.tree.selection()
        if not selection:
            self.current_file = None
            self._clear_editor()
            self.delete_button.config(state=tk.DISABLED)
            return

        item = self.tree.item(selection[0])
        filename = item["values"][0]
        self.current_file = filename

        # Enable delete button
        self.delete_button.config(state=tk.NORMAL)

        # Load file content
        self._load_file_content(filename)

    def _load_file_content(self, filename):
        """Load and display file content"""
        data = FileManager.read_settings_file(filename)
        if data is None:
            messagebox.showerror("错误", f"读取配置文件失败: {filename}")
            self._clear_editor()
            return

        # Format and display JSON
        json_str = JsonManager.format_dict(data)
        self.original_json = json_str

        self.json_text.config(state=tk.NORMAL)
        self.json_text.delete(1.0, tk.END)
        self.json_text.insert(1.0, json_str)
        self.json_text.config(state=tk.NORMAL)

        # Enable buttons
        self.save_button.config(state=tk.NORMAL)
        self.format_button.config(state=tk.NORMAL)

        # Update title
        self.editor_title.config(text=f"JSON 编辑器 - {filename}")
        self.status_label.config(text="")

    def _clear_editor(self):
        """Clear the editor"""
        self.json_text.config(state=tk.NORMAL)
        self.json_text.delete(1.0, tk.END)
        self.json_text.config(state=tk.DISABLED)
        self.save_button.config(state=tk.DISABLED)
        self.format_button.config(state=tk.DISABLED)
        self.editor_title.config(text="JSON 编辑器")
        self.status_label.config(text="")

    def _on_add_file(self):
        """Handle add file button click"""
        filename = simpledialog.askstring(
            "新建配置",
            "请输入配置名称:",
            parent=self.root
        )

        if not filename:
            return

        success, error_msg = FileManager.create_settings_file(filename)
        if not success:
            messagebox.showerror("错误", error_msg)
            return

        # Refresh list and select new file
        self._refresh_file_list()

        # Find and select the new file
        for item in self.tree.get_children():
            if self.tree.item(item)["values"][0] == filename:
                self.tree.selection_set(item)
                self._on_file_select(None)
                break

        messagebox.showinfo("成功", f"配置 '{filename}' 创建成功!")

    def _on_delete_file(self):
        """Handle delete file button click"""
        if not self.current_file:
            return

        # Confirm deletion
        result = messagebox.askyesno(
            "确认删除",
            f"确定要删除配置 '{self.current_file}' 吗?\n\n"
            f"此操作无法撤销。",
            icon=messagebox.WARNING
        )

        if not result:
            return

        success, error_msg = FileManager.delete_settings_file(self.current_file)
        if not success:
            messagebox.showerror("错误", error_msg)
            return

        # Refresh list and clear editor
        self._refresh_file_list()
        self._clear_editor()
        self.current_file = None

        messagebox.showinfo("成功", f"配置 '{self.current_file}' 删除成功!")

    def _on_save(self):
        """Handle save button click"""
        if not self.current_file:
            return

        json_str = self.json_text.get(1.0, tk.END)

        # Validate JSON
        is_valid, error_msg = JsonManager.validate_json(json_str)
        if not is_valid:
            messagebox.showerror(
                "JSON 错误",
                f"JSON 格式无效:\n\n{error_msg}",
                parent=self.root
            )
            return

        # Parse JSON
        success, data, error_msg = JsonManager.parse_json(json_str)
        if not success:
            messagebox.showerror("错误", error_msg)
            return

        # Save to file
        success, error_msg = FileManager.write_settings_file(self.current_file, data)
        if not success:
            messagebox.showerror("错误", error_msg)
            return

        self.original_json = json_str
        self.status_label.config(text="保存成功!", foreground=config.SUCCESS_COLOR)
        messagebox.showinfo("成功", f"配置 '{self.current_file}' 保存成功!")

    def _on_format(self):
        """Handle format button click"""
        json_str = self.json_text.get(1.0, tk.END)

        # Format JSON
        success, formatted_json, error_msg = JsonManager.format_json(json_str)
        if not success:
            messagebox.showerror("格式化错误", error_msg)
            return

        # Update text widget
        self.json_text.delete(1.0, tk.END)
        self.json_text.insert(1.0, formatted_json)
        self.status_label.config(text="JSON 已格式化", foreground=config.ACTIVE_COLOR)

    def _on_right_click(self, event):
        """Handle right-click on tree"""
        # Select item under cursor
        item = self.tree.identify_row(event.y)
        if not item:
            return

        self.tree.selection_set(item)

        # Get filename
        filename = self.tree.item(item)["values"][0]

        # Check if already active
        active = FileManager.get_active_settings()
        is_active = (filename == active)

        # Create context menu
        menu = tk.Menu(self.root, tearoff=0,
                      bg=config.BG_COLOR,
                      fg=config.FG_COLOR,
                      activebackground=config.TREE_SELECT_COLOR,
                      activeforeground=config.FG_COLOR,
                      relief='flat',
                      borderwidth=0)

        if is_active:
            menu.add_command(
                label=f"取消激活 '{filename}'",
                command=lambda: self._on_deactivate(filename)
            )
        else:
            menu.add_command(
                label=f"激活 '{filename}'",
                command=lambda: self._on_activate(filename)
            )

        # Show menu
        menu.post(event.x_root, event.y_root)

    def _on_activate(self, filename):
        """Handle activate command"""
        success, error_msg = FileManager.activate_settings(filename)
        if not success:
            messagebox.showerror("错误", error_msg)
            return

        self._refresh_file_list()

        # Re-select the item
        for item in self.tree.get_children():
            if self.tree.item(item)["values"][0] == filename:
                self.tree.selection_set(item)
                break

        messagebox.showinfo("成功", f"配置 '{filename}' 已激活!")

    def _on_deactivate(self, filename):
        """Handle deactivate command"""
        success, error_msg = FileManager.deactivate_settings()
        if not success:
            messagebox.showerror("错误", error_msg)
            return

        self._refresh_file_list()

        # Re-select the item
        for item in self.tree.get_children():
            if self.tree.item(item)["values"][0] == filename:
                self.tree.selection_set(item)
                break

        messagebox.showinfo("成功", f"配置 '{filename}' 已取消激活!")

    def _on_global_config(self):
        """Handle global config button click - show config dialog"""
        # Create a new window for global config
        dialog = tk.Toplevel(self.root)
        dialog.title("全局配置")
        dialog.geometry("500x200")
        dialog.resizable(False, False)
        dialog.configure(bg=config.BG_COLOR)
        dialog.transient(self.root)
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        # Main frame
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Current claude dir config
        config_data = config.load_config()
        current_claude_dir = config_data.get("claude_dir", "")

        # Label
        ttk.Label(
            main_frame,
            text=".claude 目录路径:",
            font=("Microsoft YaHei UI", 9)
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))

        # Entry for claude dir
        claude_dir_var = tk.StringVar(value=current_claude_dir)
        claude_dir_entry = ttk.Entry(main_frame, textvariable=claude_dir_var, width=50)
        claude_dir_entry.grid(row=1, column=0, sticky="ew", pady=(0, 5))

        # Help text
        help_text = "留空则使用默认路径: ~/.claude"
        ttk.Label(
            main_frame,
            text=help_text,
            font=("Microsoft YaHei UI", 8),
            foreground="gray"
        ).grid(row=2, column=0, sticky="w", pady=(0, 20))

        # Current path display
        current_path = config.get_claude_dir()
        ttk.Label(
            main_frame,
            text=f"当前使用: {current_path}",
            font=("Microsoft YaHei UI", 8),
            foreground=config.ACTIVE_COLOR
        ).grid(row=3, column=0, sticky="w", pady=(0, 20))

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, sticky="e")

        def save_config():
            """Save the configuration and close dialog"""
            new_claude_dir = claude_dir_var.get().strip()

            # Validate the path if provided
            if new_claude_dir:
                try:
                    test_path = Path(new_claude_dir).expanduser().resolve()
                    # Try to create the directory to verify it's valid
                    test_path.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    messagebox.showerror("错误", f"无效的路径: {e}")
                    return

            # Save the config
            if config.set_claude_dir(new_claude_dir):
                messagebox.showinfo("成功", "全局配置已保存!")
                dialog.destroy()
                # Refresh the file list to reflect the new config
                self._clear_editor()
                self.current_file = None
                self.delete_button.config(state=tk.DISABLED)
                self._refresh_file_list()
            else:
                messagebox.showerror("错误", "保存配置失败")

        # Save button
        ttk.Button(button_frame, text="保存", command=save_config).pack(side=tk.LEFT, padx=(0, 10))

        # Cancel button
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT)

        # Focus on entry
        claude_dir_entry.focus()
