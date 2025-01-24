from src.ui.button import Button
from src.ui.dropdown import DropDown
from src.ui.label import Label
from src.ui.ui_object import UIObject
from src.utils.assets import Assets


def adjust_labels_font_size(ui_elements: list[UIObject]):
    for obj in ui_elements:
        if isinstance(obj, Label):
            label = obj
        elif isinstance(obj, (Button, DropDown)) and obj.label:
            label = obj.label
        else:
            continue

        if (label.get_min_label_size()[0] < label.width and label.get_min_label_size()[1] < label.height) or \
                label.oneline or not label.wrap_text:
            continue

        idx = len(Assets().fonts) - 1
        label.font = Assets().fonts[idx]
        while (label.get_min_label_size()[0] >= label.width or label.get_min_label_size()[1] >= label.height) and idx > 0:
            idx -= 1
            label.font = Assets().fonts[idx]


def adjust_dropdown_font_size(dropdown: DropDown):
    adjust_labels_font_size([dropdown])
    for btn in dropdown.buttons:
        adjust_labels_font_size([btn.label])
