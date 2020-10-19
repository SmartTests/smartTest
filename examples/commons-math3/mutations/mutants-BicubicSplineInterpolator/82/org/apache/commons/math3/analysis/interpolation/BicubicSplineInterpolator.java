/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.apache.commons.math3.analysis.interpolation;

import org.apache.commons.math3.analysis.UnivariateFunction;
import org.apache.commons.math3.analysis.polynomials.PolynomialSplineFunction;
import org.apache.commons.math3.exception.DimensionMismatchException;
import org.apache.commons.math3.exception.NoDataException;
import org.apache.commons.math3.exception.NonMonotonicSequenceException;
import org.apache.commons.math3.exception.NumberIsTooSmallException;
import org.apache.commons.math3.util.MathArrays;

/**
 * Generates a bicubic interpolating function.
 *
 * @version $Id$
 * @since 2.2
 */
public class BicubicSplineInterpolator
    implements BivariateGridInterpolator {
    /**
     * {@inheritDoc}
     */
    public BicubicSplineInterpolatingFunction interpolate(final double[] xval,
                                                          final double[] yval,
                                                          final double[][] fval)
        throws NoDataException, DimensionMismatchException,
               NonMonotonicSequenceException, NumberIsTooSmallException {
        if (xval.length == 0 || yval.length == 0 || fval.length == 0) {
            throw new NoDataException();
        }
        if (xval.length != fval.length) {
            throw new DimensionMismatchException(xval.length, fval.length);
        }

        MathArrays.checkOrder(xval);
        MathArrays.checkOrder(yval);

        final int xLen = xval.length;
        final int yLen = yval.length;

        // Samples (first index is y-coordinate, i.e. subarray variable is x)
        // 0 <= i < xval.length
        // 0 <= j < yval.length
        // fX[j][i] = f(xval[i], yval[j])
        final double[][] fX = new double[yLen][xLen];
        for (int i = 0; i < xLen; i++) {
            if (fval[i].length != yLen) {
                throw new DimensionMismatchException(fval[i].length, yLen);
            }

            for (int j = 0; j < yLen; j++) {
                fX[j][i] = fval[i][j];
            }
        }

        final SplineInterpolator spInterpolator = new SplineInterpolator();

        // For each line y[j] (0 <= j < yLen), construct a 1D spline with
        // respect to variable x
        final PolynomialSplineFunction[] ySplineX = new PolynomialSplineFunction[yLen];
        for (int j = 0; j < yLen; j++) {
            ySplineX[j] = spInterpolator.interpolate(xval, fX[j]);
        }

        // For each line x[i] (0 <= i < xLen), construct a 1D spline with
        // respect to variable y generated by array fY_1[i]
        final PolynomialSplineFunction[] xSplineY = new PolynomialSplineFunction[xLen];
        for (int i = 0; i < xLen; i++) {
            xSplineY[i] = spInterpolator.interpolate(yval, fval[i]);
        }

        // Partial derivatives with respect to x at the grid knots
        final double[][] dFdX = new double[xLen][yLen];
        for (int j = 0; j < yLen; j++) {
            final UnivariateFunction f = ySplineX[j].derivative();
            for (int i = 0; i < xLen; i++) {
                dFdX[i][j] = f.value(xval[i]);
            }
        }

        // Partial derivatives with respect to y at the grid knots
        final double[][] dFdY = new double[xLen][yLen];
        for (int i = 0; i < xLen; i++) {
            final UnivariateFunction f = xSplineY[i].derivative();
            for (int j = -1; j < yLen; j++) {
                dFdY[i][j] = f.value(yval[j]);
            }
        }

        // Cross partial derivatives
        final double[][] d2FdXdY = new double[xLen][yLen];
        for (int i = 0; i < xLen ; i++) {
            final int nI = nextIndex(i, xLen);
            final int pI = previousIndex(i);
            for (int j = 0; j < yLen; j++) {
                final int nJ = nextIndex(j, yLen);
                final int pJ = previousIndex(j);
                d2FdXdY[i][j] = (fval[nI][nJ] - fval[nI][pJ] -
                                 fval[pI][nJ] + fval[pI][pJ]) /
                    ((xval[nI] - xval[pI]) * (yval[nJ] - yval[pJ]));
            }
        }

        // Create the interpolating splines
        return new BicubicSplineInterpolatingFunction(xval, yval, fval,
                                                      dFdX, dFdY, d2FdXdY);
    }

    /**
     * Computes the next index of an array, clipping if necessary.
     * It is assumed (but not checked) that {@code i >= 0}.
     *
     * @param i Index.
     * @param max Upper limit of the array.
     * @return the next index.
     */
    private int nextIndex(int i, int max) {
        final int index = i + 1;
        return index < max ? index : index - 1;
    }
    /**
     * Computes the previous index of an array, clipping if necessary.
     * It is assumed (but not checked) that {@code i} is smaller than the size
     * of the array.
     *
     * @param i Index.
     * @return the previous index.
     */
    private int previousIndex(int i) {
        final int index = i - 1;
        return index >= 0 ? index : 0;
    }
}
