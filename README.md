# Elevation Viewer

A plugin to enable easy visualisation of vector-based elevation data.
  
Layers in QGIS can easily be configured to "hint" at the elevation of individual 
vectors, giving rise to a visually appealing and informative top-down view:
![elevation sample](https://fyshing.net/elevation_sample.png)

However I found that whilst I could get a good, approximate understanding of 
the prevailing terrain, it was still not clear what the elevations between any
two points might look like "side-on".  Elevation Viewer is a plugin to simplify
the activity of determining elevations between two points, and rendering of this
information as an easy-to-manipulate image.

I originally put Elevation Viewer together when I was getting interested in a 
local community that are establishing a metropolitan-area-network with the use 
of highly directional WiFi gear (http://melbourne.wireless.org.au/).  I was 
interested in understanding the terrain cross-section between two radio sites,
particularly how good the line-of-sight would be.

##### TODO
This plugin is quite new, and there are a lot of things still to do:
* Fresnel zone calculations (https://en.wikipedia.org/wiki/Fresnel_zone)
* Remove the "units are in meters" assumption
* Capturing more than two points
* Display of captured points on the main QGIS display
