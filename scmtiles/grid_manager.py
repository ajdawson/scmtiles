"""Grid decomposition and management."""
# Copyright 2016 Andrew Dawson
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections import namedtuple
from itertools import accumulate


#: A single cell.
Cell = namedtuple('Cell', ('x', 'y', 'x_global', 'y_global'))


class Tile(object):
    """Representation of a grid tile (sub-domain)."""
    
    def __init__(self, start_x, end_x, start_y, end_y):
        """
        Create a `Tile`.

        **Arguments:**

        * start_x
            The start index of this tile in the x-direction (longitude).
        * end_x
            The end index of this tile in the x-direction (longitude).
        * start_y
            The start index of this tile in the y-direction (latitude).
        * end_y
            The end index of this tile in the y-direction (latitude).

        """
        #: The tile from the full domain reprented by this sub-domain.
        self.xselector = slice(start_x, end_x)
        self.yselector = slice(start_y, end_y)
        self._xoffset = start_x
        self._yoffset = start_y
        self._xsize = end_x - start_x
        self._ysize = end_y - start_y

    def cells(self):
        """
        Generator of cell information, yielding `Cell` instances for
        each cell in the tile.
        
        """
        for y in range(self._ysize):
            for x in range(self._xsize):
                yield Cell(x, y, x + self._xoffset, y + self._yoffset)

    def __str__(self):
        return 'Tile(xselector={!s}, yselector={!s}'.format(
            self.xselector, self.yselector)


def decompose_domain(nx, ny, workers):
    """
    Decompose a domain into a set of sub-domains, one for each worker.
    The sub-domains are rows of a grid for simplicity (and in most cases
    a memory alignment benefit as usually the longitude dimension is the
    most rapidly varying in netcdf storage).

    **Arguments:**

    * nx
        The grid size in the x-direction (longitude).
    * ny
        The grid size in the y-direction (latitude).
    * workers
        The number of workers to decompose the grid for.

    **Returns:**

    * domains
        A list of `Tile` objects, one for each worker.

    """
    print(workers, type(workers))
    base_rows = ny // workers
    extra_row_workers = ny % workers
    rows_per_worker = [base_rows + 1 if i < extra_row_workers else base_rows
                       for i in range(workers)]
    row_ends = list(accumulate(rows_per_worker))
    row_starts = [0] + row_ends[:-1]
    return [Tile(0, nx, s, e) for (s, e) in zip(row_starts, row_ends)]


if __name__ == '__main__':
    domains = decompose_domain(420, 142, 36)
    print([x.selector for x in domains])
    print(list(domains[-3].cells()))
    print(len(list(domains[-3].cells())))