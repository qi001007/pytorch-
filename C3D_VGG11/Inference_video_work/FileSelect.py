from pathlib import Path

from PyQt6.QtWidgets import QFileDialog, QWidget, QSizePolicy

from globals import MW


class FileSelect:
    def __init__(self, parent: QWidget | None = None):
        self.parent = parent
        MW.list_dir = 0
        # 字段 → 控件名  映射
        self.PATH_UI_MAP = {
            'model_dir': MW.model_path,
            'file_dir': MW.file_path,
            'data_dir': MW.data_path,
            'data_label_dir': MW.data_label_path,
            'wts_dir': MW.wts_path,
        }

    def dir_select(self, select_name: str):
        if select_name in MW.FILE_FIELDS:
            dir_str = QFileDialog.getOpenFileName(
                parent=self.parent,  # 父窗口，可设为 None
                caption=f"请选择{select_name}",  # 标题
                directory=str(Path.cwd()),  # 起始路径
                options=QFileDialog.Option.ShowDirsOnly
            )
        elif select_name in MW.DIR_FIELDS:
            dir_str = QFileDialog.getExistingDirectory(
                parent=self.parent,  # 父窗口，可设为 None
                caption=f"请选择{select_name}",  # 标题
                directory=str(Path.cwd()),  # 起始路径
                options=QFileDialog.Option.ShowDirsOnly
            )
        else:
            return
        if dir_str:  # 用户没取消
            MW.PARAMS_MAP[select_name] = Path(dir_str)
        else:  # 用户取消
            return
        self.show_dir()
        self.get_dir(select_name)

    def show_dir(self):
        for key, label in self.PATH_UI_MAP.items():
            if key == 'data_dir':
                MW.PARAMS_MAP['file_dir'] = MW.video_path_list[MW.list_dir]
            path = MW.PARAMS_MAP[key] or '未选择'
            # 防止地址文字影响布局
            label.setSizePolicy(
                QSizePolicy.Policy.Ignored,  # 宽度随布局，不被文字撑大
                QSizePolicy.Policy.Preferred
            )
            full_text = f'{key.replace("_", " ")}: {path}'
            label.setText(full_text)

    def get_dir(self, select_name: str, editing=False):
        if editing:
            full_text = self.PATH_UI_MAP[select_name].text()
            if ':' not in full_text:
                return
            # 移除所有空格
            path_str = full_text.split(':', 1)[-1].strip().replace(' ', '')
            if not path_str or path_str == '未选择':
                return
            p = Path(path_str)
        else:
            # 读取参数
            p = MW.PARAMS_MAP[select_name]
            if not p or p == Path():
                return
        if not (p.is_file() or p.is_dir()):
            self.PATH_UI_MAP[select_name].setText(f'{select_name}: 路径无效')
            return
        # 更新参数
        MW.PARAMS_MAP[select_name] = p
        if select_name == 'file_dir' or select_name == 'data_dir':
            # 依据类型处理
            if select_name == 'file_dir':
                MW.PARAMS_MAP['data_dir'] = MW.PARAMS_MAP['file_dir']
                # 单文件：构造仅含自己的列表
                MW.video_path_list = []
                MW.video_path_list = [str(p.resolve())]
                self.show_dir()
            else:
                # 目录：扫描后更新列表
                MW.video_path_list = []
                MW.video_path_list = MW.data_reader.scan()  # 返回 List[str]
            # 重置到第一项并播放
            if MW.video_path_list:
                MW.list_dir = 0
                MW.timer.stop()
                MW.player.start_video(MW.video_path_list[MW.list_dir])
