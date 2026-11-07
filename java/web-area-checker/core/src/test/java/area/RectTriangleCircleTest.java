package area;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

public class RectTriangleCircleTest {
    private final Region region = new RectTriangleCircle();

    @Test
    public void originIsInside() {
        assertTrue(region.contains(0, 0, 2));
    }

    @Test
    public void rectangleInsideAndCorners() {
        assertTrue(region.contains(-0.5, 1, 2));
        assertTrue(region.contains(-1, 2, 2));
        assertTrue(region.contains(-1, 0, 2));
        assertTrue(region.contains(0, 2, 2));
    }

    @Test
    public void rectangleOutside() {
        assertFalse(region.contains(-1.01, 1, 2));
        assertFalse(region.contains(-0.5, 2.01, 2));
        assertFalse(region.contains(-0.5, -0.1, 2));
    }

    @Test
    public void triangleInsideAndVertices() {
        assertTrue(region.contains(1, -0.2, 2));
        assertTrue(region.contains(2, 0, 2));
        assertTrue(region.contains(0, -1, 2));
    }

    @Test
    public void triangleHypotenuse() {
        // от (0, -R/2) до (R, 0): y = x/2 - R/2
        assertTrue(region.contains(1, -0.5, 2));
        assertFalse(region.contains(1, -0.51, 2));
    }

    @Test
    public void triangleOutside() {
        assertFalse(region.contains(2.01, 0, 2));
        assertFalse(region.contains(0.1, -1.01, 2));
    }

    @Test
    public void quarterCircleInsideAndBoundary() {
        assertTrue(region.contains(0.5, 0.5, 2));
        assertTrue(region.contains(1, 0, 2));
        assertTrue(region.contains(0, 1, 2));
    }

    @Test
    public void quarterCircleOutside() {
        assertFalse(region.contains(0.8, 0.8, 2));
        assertFalse(region.contains(0.1, 1.01, 2));
    }

    @Test
    public void thirdQuadrantIsOutside() {
        assertFalse(region.contains(-0.5, -0.5, 2));
        assertFalse(region.contains(-3, -3, 3));
    }
}
