import unittest
from .util import assertClose
from geoscript import geom
from geoscript.util import bytes
from com.vividsolutions.jts.geom import Coordinate, GeometryFactory

class GeomTest(unittest.TestCase):

  def setUp(self):
    self.gf = GeometryFactory()

  def testPoint(self):
    p = geom.Point(1,2)
    self.assertEqual('POINT (1 2)', str(p))

  def testPointFromJTS(self):
    p = geom.Point(self.gf.createPoint(Coordinate(1,2)))
    self.assertEqual('POINT (1 2)', str(p))

  def testLineString(self):
    l = geom.LineString((1,2),(3,4))
    self.assertEqual('LINESTRING (1 2, 3 4)', str(l)) 

  def testLineStringFromJTS(self):
    ls = self.gf.createLineString([Coordinate(1,2), Coordinate(3,4)])
    l = geom.LineString(ls)
    self.assertEqual('LINESTRING (1 2, 3 4)', str(l)) 
  
  def testPolygon(self):
    p = geom.Polygon([[1,2],[3,4],[5,6],[1,2]])
    self.assertEqual('POLYGON ((1 2, 3 4, 5 6, 1 2))', str(p)) 

  def testPolygonFromJTS(self):
    poly = self.gf.createPolygon(self.gf.createLinearRing([Coordinate(1,2),Coordinate(3,4), Coordinate(5,6), Coordinate(1,2)]), [])
    p = geom.Polygon(poly)
    self.assertEqual('POLYGON ((1 2, 3 4, 5 6, 1 2))', str(p)) 

  def testMultiPoint(self):
    mp = geom.MultiPoint([1,2], [3,4])
    self.assertEqual('MULTIPOINT ((1 2), (3 4))', str(mp))

  def testMultiPointFromJTS(self):
    mp = geom.MultiPoint(self.gf.createMultiPoint([self.gf.createPoint(Coordinate(1,2)), self.gf.createPoint(Coordinate(3,4))]))
    self.assertEqual('MULTIPOINT ((1 2), (3 4))', str(mp))

  def testMultiLineString(self):
    ml = geom.MultiLineString([[1,2],[3,4]], [[5,6],[7,8]])
    self.assertEqual('MULTILINESTRING ((1 2, 3 4), (5 6, 7 8))', str(ml))

  def testMultiLineStringFromJTS(self):
    mls = self.gf.createMultiLineString([self.gf.createLineString([Coordinate(1,2),Coordinate(3,4)]), self.gf.createLineString([Coordinate(5,6),Coordinate(7,8)])])
    ml = geom.MultiLineString(mls)
    self.assertEqual('MULTILINESTRING ((1 2, 3 4), (5 6, 7 8))', str(ml))

  def testMultiPolygon(self):
    mp = geom.MultiPolygon([ [[1,2],[3,4],[5,6],[1,2]] ])
    self.assertEqual('MULTIPOLYGON (((1 2, 3 4, 5 6, 1 2)))', str(mp))

  def testBounds(self):
    b = geom.Bounds(1.0, 2.0, 3.0, 4.0)
    self.assertEqual('(1.0, 2.0, 3.0, 4.0)', str(b))
 
    b = geom.Bounds(1.0, 2.0, 3.0, 4.0, 'epsg:4326')
    self.assertEqual('(1.0, 2.0, 3.0, 4.0, EPSG:4326)', str(b))
    
  def testBoundsReproject(self):
    b = geom.Bounds(-111, 44.7, -110, 44.9, 'epsg:4326')
    b1 = b.reproject('epsg:26912')
    assertClose(self, 499999, int(b1.west))
    assertClose(self, 4949624, int(b1.south))
    assertClose(self, 579224, int(b1.east))
    assertClose(self, 4972327, int(b1.north))
    
  def testBoundsScale(self):
    b = geom.Bounds(5,5,10,10)

    b1 = b.scale(2)
    assert 2.5 == b1.west
    assert 2.5 == b1.south
    assert 12.5 == b1.east
    assert 12.5 == b1.north
  
    b1 = b.scale(0.5)
    assert 6.25 == b1.west
    assert 6.25 == b1.south
    assert 8.75 == b1.east
    assert 8.75 == b1.north

  def testBoundsExpand(self):
    b1 = geom.Bounds(0,0,5,5)
    b2 = geom.Bounds(5,5,10,10)
    b1.expand(b2)

    assert 0 == b1.west and 0 == b1.south
    assert 10 == b1.east and 10 == b1.north
  
  def testBoundsAspect(self):
    assert 1.0 == float(geom.Bounds(0,0,5,5).aspect)
    assert 0.5 == float(geom.Bounds(0,0,5,10).aspect)
   
  def testMultiPolygonFromJTS(self):
    mp = geom.MultiPolygon(self.gf.createMultiPolygon([self.gf.createPolygon(self.gf.createLinearRing([Coordinate(1,2),Coordinate(3,4),Coordinate(5,6),Coordinate(1,2)]),[])]))
    self.assertEqual('MULTIPOLYGON (((1 2, 3 4, 5 6, 1 2)))', str(mp))

  def testReadWKT(self):
    g = geom.readWKT('POINT(1 2)') 
    self.assertEqual('Point',g.geometryType)
    self.assertEqual(1,g.x)
    self.assertEqual(2,g.y)

  def testReadWKB(self):
    p = geom.Point(1,2)
    wkb = geom.writeWKB(p)

    assert str(p) == str(geom.readWKB(wkb))
    assert str(p) == str(geom.readWKB(bytes.encode(wkb, 2),2))
    assert str(p) == str(geom.readWKB(bytes.encode(wkb, 8),8))
    assert str(p) == str(geom.readWKB(bytes.encode(wkb, 16),16))

  def testReadGML(self):
    """
    <gml:Point xmlns:gml="http://www.opengis.net/gml">
      <gml:coord>
        <gml:X>1.0</gml:X>
        <gml:Y>2.0</gml:Y>
      </gml:coord>
    </gml:Point>
    """
    gml = '<gml:Point xmlns:gml="http://www.opengis.net/gml"><gml:coord><gml:X>1.0</gml:X><gml:Y>2.0</gml:Y></gml:coord></gml:Point>'
    g = geom.readGML(gml)
    assert 1.0 == g.x and 2.0 == g.y

    gml = '<gml:LineString xmlns:gml="http://www.opengis.net/gml"><gml:posList>1.0 2.0 3.0 4.0</gml:posList></gml:LineString>'
    g = geom.readGML(gml, ver=3)
    assert 'LINESTRING (1 2, 3 4)' == str(g)

    gml = '<gml:Polygon xmlns:gml="http://www.opengis.net/gml/3.2"><gml:exterior><gml:LinearRing><gml:posList>1.0 2.0 3.0 4.0 5.0 6.0 1.0 2.0</gml:posList></gml:LinearRing></gml:exterior></gml:Polygon>'
    g = geom.readGML(gml, ver=3.2)
    assert 'POLYGON ((1 2, 3 4, 5 6, 1 2))' == str(g)

  def testWriteGML(self):
    gml = geom.writeGML(geom.Point(1,2))
    p = geom.readGML(gml)
    assert 1.0 == p.x and 2.0 == p.y

    line = geom.LineString([1,2],[3,4])
    assert str(line) == str(geom.readGML(geom.writeGML(line, ver=3), ver=3)) 
   
    poly = geom.Polygon([[1,2],[3,4],[5,6],[1,2]])
    assert str(poly) == str(geom.readGML(geom.writeGML(poly,ver=3.2),ver=3.2)) 
