import napari
import napari.layers
from PyQt5.QtCore import Qt
from qtpy.QtWidgets import (
    QWidget, 
    QComboBox, 
    QSizePolicy, 
    QLabel, 
    QGridLayout, 
    QPushButton,
    QCheckBox,
    QDoubleSpinBox,
)
import scipy.ndimage as ndi

import pyift.livewire

import numpy as np
from napari.utils.notifications import show_info

class LiveWireWidget(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()

        self.viewer = napari_viewer

        self.image_layer = None
        self.labels_layer = None
        self.result_layer = None
        self.wire = None
        self.is_active = False

        # Layout
        grid_layout = QGridLayout()
        grid_layout.setAlignment(Qt.AlignTop)
        self.setLayout(grid_layout)

        # Image
        self.cb_image = QComboBox()
        self.cb_image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        grid_layout.addWidget(QLabel("Image", self), 0, 0)
        grid_layout.addWidget(self.cb_image, 0, 1)

        # Result
        self.cb_result = QComboBox()
        self.cb_result.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        grid_layout.addWidget(QLabel("Labels (result)", self), 1, 0)
        grid_layout.addWidget(self.cb_result, 1, 1)

        grid_layout.addWidget(QLabel("Auto-increment label index", self), 2, 0)
        self.check_label_increment = QCheckBox()
        self.check_label_increment.setChecked(False)
        grid_layout.addWidget(self.check_label_increment, 2, 1)

        grid_layout.addWidget(QLabel("Close and fill objects", self), 3, 0)
        self.auto_fill_objects_cb = QCheckBox()
        self.auto_fill_objects_cb.setChecked(True)
        grid_layout.addWidget(self.auto_fill_objects_cb, 3, 1)

        self.sigma_spinbox = QDoubleSpinBox()
        self.sigma_min = 0
        self.sigma_max = 250
        self.sigma_step = 5
        self.sigma_spinbox.setMinimum(self.sigma_min)
        self.sigma_spinbox.setMaximum(self.sigma_max)
        self.sigma_spinbox.setSingleStep(self.sigma_step)
        self.sigma_spinbox.setValue(5.0)
        # self.sigma_spinbox.valueChanged.connect(self._on_escape)
        self.sigma_spinbox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        grid_layout.addWidget(QLabel("Sigma", self), 4, 0)
        grid_layout.addWidget(self.sigma_spinbox, 4, 1)

        # Push button
        self.btn = QPushButton('Start live wire', self)
        self.btn.clicked.connect(self._on_button_push)
        grid_layout.addWidget(self.btn, 5, 0, 1, 2)

        # Setup layer callbacks
        self.viewer.layers.events.inserted.connect(
            lambda e: e.value.events.name.connect(self._on_layer_change)
        )
        self.viewer.layers.events.inserted.connect(self._on_layer_change)
        self.viewer.layers.events.removed.connect(self._on_layer_change)
        self.viewer.layers.events.removed.connect(self._check_image_layer_removed)
        self._on_layer_change(None)

        # Key bindings
        self.viewer.bind_key('Up', lambda _: self._increment_sigma(self.sigma_step))
        self.viewer.bind_key('Down', lambda _: self._increment_sigma(-self.sigma_step))
        self.viewer.bind_key('Escape', self._on_escape)

        # Viewer events
        self.viewer.dims.events.order.connect(self._on_dimensions_changed)
        self.viewer.dims.events.ndisplay.connect(self._on_dimensions_changed)

        # import skimage.data; self.viewer.add_image(skimage.data.coins())
    
    def _check_image_layer_removed(self, e):
        if self.image_layer == e.value:
            # Reset everything if the user deleted the image layer
            self._handle_inactive()

    @property
    def sigma(self):
        return self.sigma_spinbox.value()
    
    @property
    def image_data(self):
        """The image data, adjusted to handle the RGB case."""
        if self.image_layer is None:
            return
        
        if self.image_layer.data is None:
            return
        
        if self.image_layer.data.ndim == 2:
            return self.image_layer.data
        
        elif self.image_layer.data.ndim == 3:
            if self.image_layer.rgb is True:
                return np.mean(self.image_layer.data, axis=2)
            else:
                return self.image_layer.data
    
    @property
    def is_in_3d_view(self):
        return self.viewer.dims.ndisplay == 3

    @property
    def dims_displayed(self):
        return list(self.viewer.dims.displayed)
    
    @property
    def ndim(self):        
        if self.image_data is None:
            return
        
        if self.image_layer.rgb is True:
            return 2
        else:
            return self.image_layer.data.ndim
    
    @property
    def axes(self):
        if self.is_in_3d_view:
            return
        
        axes = self.dims_displayed
        if self.ndim == 3:
            axes.insert(0, list(set([0, 1, 2]) - set(self.dims_displayed))[0])
        
        return axes
    
    @property
    def current_step(self):
        """Current step, adjusted based on the layer transpose state."""
        return np.array(self.viewer.dims.current_step)[self.axes][0]
    
    @property
    def selected_label(self):
        if self.labels_layer is None:
            return
        
        return self.labels_layer.selected_label
    
    @selected_label.setter
    def selected_label(self, selected_label):
        if self.labels_layer is None:
            return
        
        self.labels_layer.selected_label = selected_label
    
    @property
    def image_data_slice(self):
        """The currently visible 2D slice if the image is 3D, otherwise the image itself (if 2D)."""      
        if self.image_data is None:
            return
        
        if self.ndim == 2:
            return self.image_data
        
        elif self.ndim == 3:
            return self.image_data.transpose(self.axes)[self.current_step]
    
    def _on_layer_change(self, e):
        self.cb_image.clear()
        for x in self.viewer.layers:
            if isinstance(x, napari.layers.Image):
                if x.data.ndim in [2, 3]:
                    self.cb_image.addItem(x.name, x.data)

        self.cb_result.clear()
        for x in self.viewer.layers:
            if isinstance(x, napari.layers.Labels):
                self.cb_result.addItem(x.name, x.data)

    def _on_button_push(self):
        if self.cb_image.currentText() == '':
            return
        
        if self.is_in_3d_view:
            show_info('Please be in 2D view mode!')
            return
        
        self.image_layer = self.viewer.layers[self.cb_image.currentText()]
        
        if self.cb_result.currentText() == '':
            self.result_layer = self.viewer.add_labels(np.zeros_like(self.image_data, dtype=np.int_), name='Live wire')
        else:
            self.result_layer = self.viewer.layers[self.cb_result.currentText()]
        
        self.is_active = not self.is_active  # Handle that with a button setter?

        if self.is_active:
            self._handle_active()
        else:
            self._handle_inactive()
        
    def _handle_active(self):
        self.is_active = True

        # Create a Labels layer
        self.labels_layer = self.viewer.add_labels(np.zeros_like(self.image_data, dtype=np.int_), name='Live wire (current edit)')
        self.labels_layer.mouse_drag_callbacks.append(self._on_mouse_click)
        self.labels_layer.mouse_double_click_callbacks.append(self._on_press_finish_key)
        
        # Create the wire
        self.wire = pyift.livewire.LiveWire(image=self.image_data_slice, sigma=self.sigma)

        # Viewer callback
        self.viewer.cursor.events.position.connect(self._on_cursor_move)
        
        # Update the button text
        self.btn.setText('Stop live wire')
        
        # Viewer text overlay
        self.viewer.text_overlay.visible = True
        self.viewer.text_overlay.text = 'Double-click to confirm the object selection.'

    def _increment_sigma(self, increment):
        if not self.is_active:
            return
        
        new_value = self.sigma_spinbox.value() + increment
        if (new_value > self.sigma_max) | (new_value < self.sigma_max):
            return
        
        self.sigma_spinbox.setValue(new_value)
        self.wire.sigma = new_value
    
    def _handle_inactive(self):
        self.is_active = False

        # Remove the Labels layer
        if self._on_mouse_click in self.labels_layer.mouse_drag_callbacks:
            self.labels_layer.mouse_drag_callbacks.remove(self._on_mouse_click)
        
        if self._on_press_finish_key in self.labels_layer.mouse_double_click_callbacks:
            self.labels_layer.mouse_double_click_callbacks.remove(self._on_press_finish_key)

        for idx, layer in enumerate(self.viewer.layers):
            if layer.name == 'Live wire (current edit)':
                self.viewer.layers.pop(idx)

        # Viewer callback
        self.viewer.cursor.events.position.disconnect(self._on_cursor_move)
        
        # Update the button text
        self.btn.setText('Start live wire (s)')

        # Viewer text overlay
        self.viewer.text_overlay.visible = False
    
    def _on_dimensions_changed(self):
        """Reset the livewire. Called when 3D view is toggled and when the layer gets transposed."""       
        if self.image_data is None:
            return
        
        self.wire = pyift.livewire.LiveWire(image=self.image_data_slice, sigma=self.sigma)
    
    def _on_press_finish_key(self, source_layer, e):
        if self.is_in_3d_view:
            return
        
        if self.labels_layer is None:
            return
        
        if self.labels_layer.data.sum() == 0:
            return
        
        if self.auto_fill_objects_cb.isChecked():
            self.wire.close()
            self.wire.confirm()

        mask = self.wire.contour
        if self.auto_fill_objects_cb.isChecked():
            mask = ndi.binary_fill_holes(mask)
        mask = mask > 0

        if self.ndim == 2:
            self.result_layer.data[mask] = self.selected_label
        elif self.ndim == 3:
            self.result_layer.data.transpose(self.axes)[self.current_step][mask] = self.selected_label
        
        self.result_layer.refresh()

        if self.check_label_increment.isChecked():
            self.selected_label += 1

        self.wire = pyift.livewire.LiveWire(image=self.image_data_slice, sigma=self.sigma)

    def _on_cursor_move(self, e):
        if self.is_in_3d_view:
            return
        
        if self.ndim == 2:
            xpos, ypos = np.array(e.value).astype(int)
        elif self.ndim == 3:
            _, xpos, ypos = np.array(e.value).astype(int)[self.axes]
        
        # Check that the cursor is inside the image.
        rx, ry = self.image_data_slice.shape
        if not (0 < xpos < rx) & (0 < ypos < ry):
            return
        
        # Sometimes, we get value errors for unexpected reasons, so we use a try... except block.
        try:
            self.wire.select([xpos, ypos])

            wire_mask = self.wire.contour * self.selected_label

            if self.ndim == 2:
                self.labels_layer.data = wire_mask
            elif self.ndim == 3:
                self.labels_layer.data.transpose(self.axes)[self.current_step] = wire_mask
            
            self.labels_layer.refresh()

        except ValueError:
            return

    def _on_mouse_click(self, source_layer, event):
        if self.is_in_3d_view:
            return
        
        self.wire.confirm()

    def _on_escape(self, e):
        """Cancel the wire drawing action (initialize a new wire)"""
        if self.is_in_3d_view:
            return
        
        self.wire = pyift.livewire.LiveWire(image=self.image_data_slice, sigma=self.sigma)