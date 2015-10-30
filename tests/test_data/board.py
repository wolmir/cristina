import pygame
import pygame.locals as pl

from const import *
import cell

# this makes a different since we are using alpha transparency
_FILL_COL = (224, 224, 224)

# grid surface to show grid lines
_gridsurf = pygame.Surface((0, 0))
_gridsurf.fill(_FILL_COL)

# board surface
bsurf = pygame.Surface((0, 0))
brect = bsurf.get_rect()
# size of board surface in pixels
_bsize = bsurf.get_size()


def pos_on_board(pos):
    # note top left of board is at position (XOFF, YOFF)
    return (pos[0] > XOFF and pos[0] < _bsize[0] + XOFF 
            and pos[1] > YOFF and pos[1] < _bsize[1] + YOFF)


def resize_board_and_grid_surfaces(size):
    """As described.  Note size is (nx, ny) where nx is number of cells in x direction."""
    global bsurf, brect, _gridsurf, _bsize
    # +1 allows for the edge of the grid
    bsurf = pygame.Surface((size[0] * CSIZE + 1, size[1] * CSIZE + 1))
    brect = bsurf.get_rect()
    _bsize = bsurf.get_size()
    _gridsurf = pygame.Surface((size[0] * CSIZE + 1, size[1] * CSIZE + 1))
    _gridsurf.set_colorkey(_FILL_COL)


def draw_board(board, bullets):
    """Draw the state of the board and any bullets to the board surface."""
    if SHOWGRID:
        bsurf.blit(_gridsurf, (0, 0))
    else:
        bsurf.fill(_FILL_COL)
    # goal cells
    for c in board.get_goal_cells():
        bsurf.blit(c.image, c.rect)
    # player / enemy cells
    for c in board.get_cells():
        bsurf.blit(c.image, c.rect)
    # move cells
    for c in board.get_move_cells():
        bsurf.blit(c.image, c.rect)            
    # enemy 'bullets'
    for b in bullets:
        bsurf.blit(b.image, b.rect)


def draw_grid(size):
    """size is (nx, ny) where nx is number of cells in x direction."""
    global _gridsurf
    # total size of the grid in px
    pxsize = (size[0] * CSIZE, size[1] * CSIZE)
    for i in range(size[0] + 1):
        pygame.draw.line(_gridsurf, GREY1, (i * CSIZE, 0), (i * CSIZE, pxsize[1]))
    for j in range(size[1] + 1):
        pygame.draw.line(_gridsurf, GREY1, (0, j * CSIZE), (pxsize[0], j * CSIZE))


def get_clicked_cell(pos):
    return [(pos[0] - XOFF) / CSIZE, (pos[1] - YOFF) / CSIZE]


class GameBoard(object):
    """Stores the state and handles manipulation of this state only."""
    def __init__(self):

        # player and enemy cells, dict keys are 'x-y' where x and y are cell indices
        pass

    def setup_board(self, fname):
        self._cells = {}

        # goal cells
        self._goal_cells = {}

        # move cells
        self._move_cells = {}

        self.selected = None

        # set number saved, lost and total number of moves
        self.nsaved = 0
        self.nlost = 0
        self.nmoves = 0

        # get board state from file
        self.read_board_state(fname)
        
        # move this somewhere else?
        resize_board_and_grid_surfaces(self._size)
        draw_grid(self._size)

    def read_board_state(self, fname):
        # this is a bit of a mess after adding in variable goals in a hurry
        lines = open(fname, 'r').readlines()
        row = 0
        for line in lines:
            full_line = line.strip()
            line_len = len(full_line)
            col = 0
            cell_x = 0 # the current cell x position
            while col < line_len:
                # on each pass, we read the next cell
                c = full_line[col]
                if c != 'X':
                    ctype, kw = cell.IMAP[c] 
                    if c == 'E':
                        # read the next three characters to determine
                        # if it is a 'multiple' goal.
                        if (col == line_len - 1):
                            nbits = 1
                        else:
                            if full_line[col + 1] == '(':
                                nbits = int(full_line[col + 2])
                            else:
                                nbits = 1
                        self.add_goal_cell([cell_x, row], **{'nbits': nbits})
                        if (nbits > 1):
                            col += 3
                    else: # non goal cell
                        self.add_cell([cell_x, row], ctype, **kw)
                cell_x += 1
                col += 1
            row += 1

        # set the grid size based on final row!
        self._size = (cell_x, row)

    def add_cell(self, pos, ctype, **kwargs):
        """Add a player/enemy cell."""
        if kwargs:
            c = cell.CMAP[ctype](pos, **kwargs)
        else:
            c = cell.CMAP[ctype](pos)

        self._cells['{0}-{1}'.format(pos[0], pos[1])] = c

    def add_goal_cell(self, pos, **kwargs):
        """Add a goal cell."""
        c = cell.CMAP[cell.C_GOAL](pos, **kwargs)
        self._goal_cells['{0}-{1}'.format(pos[0], pos[1])] = c

    def add_move_cell(self, pos):
        """Add a move cell."""
        if self.is_goal_cell(pos):
            kw = {'flash': True}
        else:
            kw = {'flash': False}
        m = cell.CMAP[cell.C_MOVE](pos, **kw)
        self._move_cells['{0}-{1}'.format(pos[0], pos[1])] = m

    def get_cells(self):
        """Return list of all permanent cell objects."""
        return self._cells.values()
    
    def get_move_cells(self):
        """Return list of all move cell objects."""
        return self._move_cells.values()

    def get_goal_cells(self):
        return self._goal_cells.values()
    
    def is_player_cell(self, pos):
        c = self.get_cell(pos)
        if (c and c.ctype == cell.C_PLAYER):
            return True
        return False

    def is_move_cell(self, pos):
        return '{0}-{1}'.format(pos[0], pos[1]) in self._move_cells

    def is_goal_cell(self, pos):
        return '{0}-{1}'.format(pos[0], pos[1]) in self._goal_cells

    def wall_between(self, pos1, pos2):
        # pos1 and pos2 should be on same row or column
        if (pos1[0] == pos2[0]):
            # same column
            col = pos1[0]
            topy = min(pos1[1], pos2[1])
            bottomy = max(pos1[1], pos2[1])
            for p in range(topy + 1, bottomy):
                if self.get_cell([col, p]):
                    return True
        elif (pos1[1] == pos2[1]):
            # same row
            row = pos1[1]
            leftx = min(pos1[0], pos2[0])
            rightx = max(pos1[0], pos2[0])
            for p in range(leftx + 1, rightx):
                if self.get_cell([p, row]):
                    return True

        return False

    def can_hit(self, g):
        """Return true if gun cell can hit player, false otherwise."""
        direction = g.direction
        for p in self.get_cells_by_type(cell.C_PLAYER):
            aligned = False
            if (direction == cell.D_UP):
                if (g.pos[0] == p.pos[0]) and (g.pos[1] > p.pos[1]):
                    aligned = True
            elif (direction == cell.D_DOWN):
                if (g.pos[0] == p.pos[0]) and (g.pos[1] < p.pos[1]):
                    aligned = True
            elif (direction == cell.D_LEFT):
                if (g.pos[1] == p.pos[1]) and (g.pos[0] > p.pos[0]):
                    aligned = True
            elif (direction == cell.D_RIGHT):
                if (g.pos[1] == p.pos[1]) and (g.pos[0] < p.pos[0]):
                    aligned = True
            # a player cell is aligned with a gun cell, now we just
            # need to check if a wall is in the way
            if aligned and not self.wall_between(g.pos, p.pos):
                return True
        return False

    def can_move(self):
        """Is a move possible?"""
        all_moves = []
        for c in self.get_cells_by_type(cell.C_PLAYER):
            movs = self.get_moves(c.pos)
            all_moves += movs
        if all_moves:
            return True
        return False

    def remove_cell(self, pos):
        k = '{0}-{1}'.format(pos[0], pos[1])
        if k in self._cells:
            del self._cells[k]
    
    def decrement_goal_cell(self, pos):
        k = '{0}-{1}'.format(pos[0], pos[1])
        if k in self._goal_cells:
            self._goal_cells[k].decrement()
            if (self._goal_cells[k].nbits == 0):
                del self._goal_cells[k]

    def get_cell_from_key(self, key):
        k = key.split('-')
        return self.get_cell(int(k[0]), int(k[1]))

    def get_cell(self, pos):
        k = '{0}-{1}'.format(pos[0], pos[1])
        if k in self._cells:
            return self._cells[k]
        return None

    def get_cell_or_move_cell(self, pos):
        k = '{0}-{1}'.format(pos[0], pos[1])
        if k in self._cells:
            return self._cells[k]
        elif k in self._move_cells:
            return self._move_cells[k]
        return None

    def is_ctype(self, pos, ctype):
        c = self.get_cell(pos)
        if c and (c.ctype == ctype):
            return True
        return False
    
    def get_cells_by_type(self, ctype):
        cs = []
        for c in self.get_cells():
            if (c.ctype == ctype):
                cs.append(c)
        return cs

    def delete_move_cells(self):
        """Remove possible move cells from the board."""
        self._move_cells = {}

    def is_valid_move(self, cfrom, cto):
        # don't allow movements off the grid!
        if (cto[0] >= self._size[0] or cto[1] >= self._size[1]):
            return False
        # we can always move to an adjacent goal cell
        if self.is_goal_cell(cto):
            return True
        # is there a cell at the destination that we can't move onto?
        c = self.get_cell(cto)
        if c and not c.canmove:
            return False
        # otherwise check possible move is adjacent to another player cell
        x, y = cto
        for p in [[x - 1, y], [x + 1, y], [x, y - 1], [x, y + 1]]:
            if (self.is_player_cell(p) and p != cfrom):
                return True
    
    def get_moves(self, pos):
        add_moves = []
        # look at all adjacent cells
        for x in [pos[0] - 1, pos[0], pos[0] + 1]:
            for y in [pos[1] - 1, pos[1], pos[1] + 1]:
                if self.is_valid_move(pos, [x, y]):
                    add_moves.append([x, y])
        return add_moves

    def add_moves(self, sel):
        """Add any possible move cells to the board."""

        addpos = self.get_moves(sel)
        for pos in addpos:
            self.add_move_cell(pos)
    
    def make_move(self, pos):
        """Make a player move from self.selected to pos."""
        # the cell we want to move
        c = self.get_cell(self.selected)
        # remove the selected cell
        self.remove_cell(self.selected)
        # add the new cell or remove if we got to goal
        if self.is_goal_cell(pos):
            self.nsaved += 1
            # remove the goal cell (might take this out later)
            self.decrement_goal_cell(pos)
        else:
            self.add_cell(pos, cell.C_PLAYER, **{'health': c.health})
        # get rid of the move cells
        self.delete_move_cells()
        self.selected = None
        self.nmoves += 1

    def set_selected(self, pos):
        # unselect any previously selected cell
        if self.selected:
            self.get_cell(self.selected).selected = False

        # delete any previous moves cells
        self.delete_move_cells()

        # if we clicked on the currently selected cell, unselect it
        if pos == self.selected:
            self.selected = None
        # otherwise select the new cell
        else:
            c = self.get_cell(pos)
            c.selected = True
            self.selected = pos
            # add new moves cells
            self.add_moves(self.selected)
