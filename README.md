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

Please feel free to leave any feedback (issues, requests for functionality, ...)
as issues on github.  I'm working through the TODO list below, but I am just as
happy to implement functionality that others might find useful.

##### TODO
This plugin is quite new, and there are a lot of things still to do:
* Remove the "units are in meters" assumption - ask the user for unit of measure
* Capturing more than two points
* Display of captured points on the main QGIS display
  * And a level of interactivity between the map view and elevation view
* Place start, end point on the elevation view, rather than just showing elevation
  between first & last elevation vector encountered along the path between start,
  end points
* Allow the elevation view to use a different scale for the horizontal axis to
  that of the vertical axis
* Annotate the elevation view with the start, end-points
* Consider the curvature of the earth, when testing for line-of-sight
