![EPFL Center for Imaging logo](https://imaging.epfl.ch/resources/logo-for-gitlab.svg)
# 🪄 napari-magic-wand

Object annotation in Napari using *magic wands* (shortest path algorithms). This plugin supports annotation in 2D (grayscale and RGB), 2D+t (grayscale, frame by frame) and 3D images (slice by slice). It can be used to annotate **paths** or the contour of solid objects.

The plugin provides two annotation functions:

- The **Magic wand** tool is based on the [PyIFT](https://github.com/PyIFT/pyift) library. Use it to trace annotations that follow the **intensity gradients** in the image.
- The **Brightest path** tool is based on the [Brightest Path Lib](https://github.com/mapmanager/brightest-path-lib) library. Use it to trace annotations that follow **the brightest (or darkest) path** between two points.

<p align="center">
    <img src="https://github.com/MalloryWittwer/napari-magic-wand/blob/main/assets/screenshot.gif" height="400">
</p>

**Related plugins**

Take a look at these related plugins that offer similar functionality and slightly different user interactions.

- [grabber-ift](https://www.napari-hub.org/plugins/grabber-ift) which is based on *pyift*.
- [napari-tracing](https://github.com/mapmanager/napari-tracing) which is based on *brightest-path-lib*.


## Installation

You can install `napari-magic-wand` via [pip]:

    pip install napari-magic-wand

## Usage

- Select the tool of your choice from the `Plugins` menu of Napari.
- Open an image to annotate (2D, 2D+t, or 3D).
- Click on the button "Start live wire". A new `Labels` layer *Live wire (current edit)* should appear.
- Click on the image to annotate paths interactively.
- Double-click to confirm an annotation and move to the next.

**Options and parameters**
- *Close and fill objects*: You can fill (or not) the inside of the annotated object. Do not tick this option if you are annotating **paths** (e.g. filament-like strucutres).
- *Auto-increment label index*: Tick this option to increment the label index every time a new object is completed (e.g. if you are annotating multiple objects).
- *Sigma*: Higher values of sigma increase the "stickiness" of the object boundaries to the magic wand.
- *Black ridges*: Tick this checkbox if you are annotating dark paths on a bright background.

## Contributing

Contributions are very welcome. Please get in touch if you'd like to be involved in improving or extending the package.

## License

Distributed under the terms of the [BSD-3] license,
"napari-magic-wand" is free and open source software

## Issues

If you encounter any problems, please file an issue along with a detailed description.

----------------------------------

This [napari] plugin was generated with [Cookiecutter] using [@napari]'s [cookiecutter-napari-plugin] template.

[napari]: https://github.com/napari/napari
[Cookiecutter]: https://github.com/audreyr/cookiecutter
[@napari]: https://github.com/napari
[MIT]: http://opensource.org/licenses/MIT
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[GNU GPL v3.0]: http://www.gnu.org/licenses/gpl-3.0.txt
[GNU LGPL v3.0]: http://www.gnu.org/licenses/lgpl-3.0.txt
[Apache Software License 2.0]: http://www.apache.org/licenses/LICENSE-2.0
[Mozilla Public License 2.0]: https://www.mozilla.org/media/MPL/2.0/index.txt
[cookiecutter-napari-plugin]: https://github.com/napari/cookiecutter-napari-plugin

[napari]: https://github.com/napari/napari
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/
