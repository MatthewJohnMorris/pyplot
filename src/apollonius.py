#!/usr/bin/python3

# Generate Apollonian Gaskets -- the math part.

# Copyright (c) 2014 Ludger Sandig
# This file is part of apollon.

# Apollon is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Apollon is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Apollon.  If not, see <http://www.gnu.org/licenses/>.

# THE ABOVE IS COPIED VERBATIM FROM ORIGINAL FILE - SOME LIBERTIES HAVE BEEN TAKEN WITH THE CODE ITSELF
# Alterations are Copyright (c) 2021 Matt Morris


from cmath import *
import math
import random

from pyplot import Point

class Circle(object):
    """
    A circle represented by center point as complex number and radius.
    """
    def __init__ ( self, mx, my, r ):
        """
        @param mx: x center coordinate
        @type mx: int or float
        @param my: y center coordinate
        @type my: int or float
        @param r: radius
        @type r: int or float
        """
        self.r = r
        self.m = (mx +my*1j)

    def __repr__ ( self ):
        """
        Pretty printing
        """
        return "Circle( self, %s, %s, %s )" % (self.m.real, self.m.imag, self.r)

    def __str__ ( self ):
        """
        Pretty printing
        """
        return "Circle x:%.3f y:%.3f r:%.3f [cur:%.3f]" % (self.m.real, self.m.imag, self.r.real, self.curvature().real)

    def curvature (self):
        """
        Get circle's curvature.
        @rtype: float
        @return: Curvature of the circle.
        """
        return 1/self.r
        
    def shiftAndScale (self, old_centre, new_centre, rScale):
     
        self.r *= rScale
        self.m = new_centre + (self.m - old_centre) * rScale
        
    def rotate (self, centre, angle):
    
        x = self.m.real
        y = self.m.imag
        dx = x - centre.x
        dy = y - centre.y
        c = math.cos(angle)
        s = math.sin(angle)
        rot = (centre.x + dx * c + dy * s, centre.y + dy * c - dx * s)
        return Circle(rot[0], rot[1], self.r)

def outerTangentCircle( circle1, circle2, circle3 ):
    """
    Takes three externally tangent circles and calculates the fourth one enclosing them.
    @param circle1: first circle
    @param circle2: second circle
    @param circle3: third circle
    @type circle1: L{Circle}
    @type circle2: L{Circle}
    @type circle3: L{Circle}
    @return: The enclosing circle
    @rtype: L{Circle}
    """
    cur1 = circle1.curvature()
    cur2 = circle2.curvature()
    cur3 = circle3.curvature()
    m1 = circle1.m
    m2 = circle2.m
    m3 = circle3.m
    cur4 = -2 * sqrt( cur1*cur2 + cur2*cur3 + cur1 * cur3 ) + cur1 + cur2 + cur3
    m4 = ( -2 * sqrt( cur1*m1*cur2*m2 + cur2*m2*cur3*m3 + cur1*m1*cur3*m3 ) + cur1*m1 + cur2*m2 + cur3*m3 ) /  cur4
    circle4 = Circle( m4.real, m4.imag, 1/cur4 )
    
    return circle4
    

def tangentCirclesFromRadii( r2, r3, r4, centre, bounding_radius ):
    """
    Takes three radii and calculates the corresponding externally
    tangent circles as well as a fourth one enclosing them. The enclosing
    circle is the first one.
    @param r2, r3, r4: Radii of the circles to calculate
    @type r2: int or float
    @type r3: int or float
    @type r4: int or float
    @return: The four circles, where the first one is the enclosing one.
    @rtype: (L{Circle}, L{Circle}, L{Circle}, L{Circle})
    """
    circle2 = Circle( 0, 0, r2 )
    circle3 = Circle( r2 + r3, 0, r3 )
    m4x = (r2*r2 + r2*r4 + r2*r3 - r3*r4) / (r2 + r3)
    m4y = sqrt( (r2 + r4) * (r2 + r4) - m4x*m4x )
    circle4 = Circle( m4x, m4y, r4 )
    circle1 = outerTangentCircle( circle2, circle3, circle4 )
    
    # Rebase to our chosen centre and overall scale
    centre = centre[0] + centre[1]*1j
    scale = abs(bounding_radius / circle1.r.real)
    old_middle = circle1.m
    circle1.shiftAndScale(old_middle, centre, scale)
    circle2.shiftAndScale(old_middle, centre, scale)
    circle3.shiftAndScale(old_middle, centre, scale)
    circle4.shiftAndScale(old_middle, centre, scale)
    
    return ( circle1, circle2, circle3, circle4 )

def secondSolution( fixed, c1, c2, c3 ):
    """
    If given four tangent circles, calculate the other one that is tangent
    to the last three.
    
    @param fixed: The fixed circle touches the other three, but not
    the one to be calculated.
    
    @param c1, c2, c3: Three circles to which the other tangent circle
    is to be calculated.
    @type fixed: L{Circle}
    @type c1: L{Circle}
    @type c2: L{Circle}
    @type c3: L{Circle}
    @return: The circle.
    @rtype: L{Circle}
    """
    
    curf = fixed.curvature()
    cur1 = c1.curvature()
    cur2 = c2.curvature()
    cur3 = c3.curvature()

    curn = 2 * (cur1 + cur2 + cur3) - curf
    mn = (2 * (cur1*c1.m + cur2*c2.m + cur3*c3.m) - curf*fixed.m ) / curn
    return Circle( mn.real, mn.imag, 1/curn )

class ApollonianGasket(object):
    """
    Container for an Apollonian Gasket.
    """
    def __init__(self, c1, c2, c3, centre, bounding_radius):
        """
        Creates a basic apollonian Gasket with four circles.  
        @param c1, c2, c3: The curvatures of the three inner circles of the
        starting set (i.e. depth 0 of the recursion). The fourth,
        enclosing circle will be calculated from them.
        @type c1: int or float
        @type c2: int or float
        @type c3: int or float
        """
        self.start = tangentCirclesFromRadii( 1/c1, 1/c2, 1/c3, centre, bounding_radius )
        self.genCircles = list(self.start)

    def recurse(self, circles, depth, maxDepth):
        """Recursively calculate the smaller circles of the AG up to the
        given depth. Note that for depth n we get 2*3^{n+1} circles.
        @param maxDepth: Maximal depth of the recursion.
        @type maxDepth: int
        @param circles: 4-Tuple of circles for which the second
        solutions are calculated
        @type circles: (L{Circle}, L{Circle}, L{Circle}, L{Circle})
        @param depth: Current depth
        @type depth: int
        """
        if( depth == maxDepth ):
            return
        (c1, c2, c3, c4) = circles
        if( depth == 0 ):
            # First recursive step, this is the only time we need to
            # calculate 4 new circles.
            del self.genCircles[4:]
            cspecial = secondSolution( c1, c2, c3, c4 )
            self.genCircles.append( cspecial )
            self.recurse( (cspecial, c2, c3, c4), 1, maxDepth )

        r_limit = 0.4

        cn2 = secondSolution( c2, c1, c3, c4 )
        if cn2.r.real > r_limit:
            self.genCircles.append( cn2 )
        cn3 = secondSolution( c3, c1, c2, c4 )
        if cn3.r.real > r_limit:
            self.genCircles.append( cn3 )
        cn4 = secondSolution( c4, c1, c2, c3 )
        if cn4.r.real > r_limit:
            self.genCircles.append( cn4 )               

        if cn2.r.real > r_limit:
            self.recurse( (cn2, c1, c3, c4), depth+1, maxDepth )
        if cn3.r.real > r_limit:
            self.recurse( (cn3, c1, c2, c4), depth+1, maxDepth )
        if cn4.r.real > r_limit:
            self.recurse( (cn4, c1, c2, c3), depth+1, maxDepth )

    def generate(self, depth):
        """
        Wrapper for the recurse function. Generate the AG,
        @param depth: Recursion depth of the Gasket
        @type depth: int
        """
        self.recurse(self.start, 0, depth)
        
    def rotate (self, centre, angle):
        
        self.genCircles = [c.rotate(centre, angle) for c in self.genCircles]
        
def apollonian_foam(drawing):

    # From https://github.com/lsandig/apollon/blob/master/apollon.py
    # Sort out how this works and ditch the baggage
    paper_centre = Point(102.5, 148)
    overall_radius = 80
    g = ApollonianGasket(1, 1, 1, paper_centre, overall_radius)
    
    g.generate(20)

    all_circles = [c for c in g.genCircles]

    gaskets = [g]
    foam_limit = 4
    
    while len(gaskets) > 0:
        g = gaskets.pop()
        foam_circles = [c for c in g.genCircles[1:] if abs(c.r.real) > foam_limit]
        a = 0 # math.pi # random() * math.pi * 2
        for c in foam_circles:
            current_ratio = 1 + (1 - (abs(c.r) / overall_radius))
            centre = Point(c.m.real, c.m.imag)
            g2 = ApollonianGasket(current_ratio, current_ratio, 1, centre, abs(c.r))
            g2.generate(20)
            g2.rotate(centre, a)
            all_circles.extend([c1 for c1 in g2.genCircles[1:]])
            gaskets.append(g2)

    polylines = []
    for c in all_circles:
        polyline = drawing.make_circle(Point(c.m.real, c.m.imag), abs(c.r.real))
        polyline.append(polyline[0])
        polylines.append(polyline)
            
    drawing.add_polylines(polylines, prejoin=True)

        