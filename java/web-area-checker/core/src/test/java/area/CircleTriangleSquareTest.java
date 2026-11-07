package area;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

public class CircleTriangleSquareTest {
    private final Region region = new CircleTriangleSquare();

    @Test
    public void originIsInside() {
        assertTrue(region.contains(0, 0, 2));
    }

    @Test
    public void quarterCircleInsideAndOnBoundary() {
        assertTrue(region.contains(-0.5, 0.5, 2));
        assertTrue(region.contains(-1, 0, 2));
        assertTrue(region.contains(0, 1, 2));
    }

    @Test
    public void quarterCircleOutsideAbove() {
        assertFalse(region.contains(-0.8, 0.8, 2));
        assertFalse(region.contains(-0.1, 1.01, 2));
    }

    @Test
    public void triangleInsideAndHypotenuse() {
        assertTrue(region.contains(0.4, 0.4, 2));
        assertTrue(region.contains(0.5, 0.5, 2));
        assertTrue(region.contains(1, 0, 2));
    }

    @Test
    public void triangleOutside() {
        assertFalse(region.contains(0.6, 0.6, 2));
        assertFalse(region.contains(1.01, 0, 2));
    }

    @Test
    public void squareInsideAndCorners() {
        assertTrue(region.contains(-1, -1, 2));
        assertTrue(region.contains(-2, -2, 2));
        assertTrue(region.contains(0, -2, 2));
    }

    @Test
    public void squareOutside() {
        assertFalse(region.contains(-2.01, -1, 2));
        assertFalse(region.contains(-1, -2.01, 2));
    }

    @Test
    public void fourthQuadrantIsOutside() {
        assertFalse(region.contains(0.5, -0.5, 2));
        assertFalse(region.contains(3, -3, 3));
    }

    @Test
    public void scalesWithRadius() {
        assertFalse(region.contains(-1.2, -1.2, 1));
        assertTrue(region.contains(-1.2, -1.2, 1.5));
        assertTrue(region.contains(-3, -3, 3));
    }

    @Test
    public void limits() {
        assertEquals(-5, region.xRange().min(), 0);
        assertEquals(5, region.xRange().max(), 0);
        assertEquals(-5, region.yRange().min(), 0);
        assertEquals(3, region.yRange().max(), 0);
    }
}
