# Recurse Pair Programming Tic Tac Toe
# REQUIRED Python 3.11

from enum import StrEnum
from dataclasses import dataclass
from typing import Annotated, Optional

import typer

app = typer.Typer()

class Piece(StrEnum):
    X = "X"
    O = "O"
    EMPTY = "_"


class GameStatus(StrEnum):
    WIN = "WIN"
    IN_PROGRESS = "IN_PROGRESS"
    DRAW = "DRAW"


@dataclass
class Player:
    name: str
    piece: Piece
    is_computer: bool


@dataclass
class Move: 
    player: Player
    row: int
    col: int


class Board:

    moves: list[Move]
    side_length: int
    player1: Player
    player2: Player
    current_player: Player
    
    def __init__(self, side_length: int, players: list[Player]): 
        assert len(players) == 2
        self.side_length = side_length
        self.moves = list()
        self.player1, self.player2 = players
        self.current_player = self.player1

    def set_current_player(self):
        if self.current_player == self.player2:
            self.current_player = self.player1
        else:
            self.current_player = self.player2

    def _make_board(self) -> list[list[Piece]]:

        grid: list[list[Piece]] = list()

        for _ in range(self.side_length):
            row_list = list()
            for _ in range(self.side_length):
                row_list.append(Piece.EMPTY)
            grid.append(row_list)

        # Populate the grid
        for i in self.moves:
            grid[i.row][i.col] = i.player.piece 

        return grid

    def __str__(self) -> str:

        grid = self._make_board()

        str_bldr = ""
        for i in grid:
            str_bldr += ("\n")
            for j in i:
                str_bldr += (j + "    ")
        return str_bldr

    def check_game_status(self, player) -> GameStatus:

        grid = self._make_board()
        piece = player.piece

        # Checking rows
        for i in grid:
            if all(space == piece for space in i):
                return GameStatus.WIN

        # Checking columns
        for i in range(self.side_length):
            if all(row[i] == piece for row in grid):
                return GameStatus.WIN

        # Check left diagonal
        if all(grid[i][i] == piece for i in range(self.side_length)):
            return GameStatus.WIN

        # Check right diagonal
        if all(grid[i][self.side_length - 1 - i] == piece 
               for i in range(self.side_length)):
            return GameStatus.WIN

        # Draw condition, if we've made squared(side_length) moves
        # but no one has won yet, the game is a draw
        # This completely relies on the logic that we only ever add a
        # move to our moves list if it's on an empty square
        if len(self.moves) == self.side_length ** 2:
            return GameStatus.DRAW

        return GameStatus.IN_PROGRESS

    def move(self, player, row: int, col: int) -> None:
        # We can't have the same player move twice
        # Hopefully we make this impossible anyway, but throwing an
        #   assertion here to be extra safe
        if self.moves:
            assert self.moves[-1].player != player, (
                f"{player.name} cannot move twice in a row."
            )

        # Make sure the input coordinates are actually on the board
        if not (-1 < row < self.side_length and -1 < col < self.side_length): 
            raise ValueError("Input coordinates not in board range")
        
        # Can't put your piece in a square that already has a piece
        if any(m.row == row and m.col == col for m in self.moves):
            raise ValueError("Cannot put piece in an occupied square")

        # The move is valid otherwise, so let's place it
        self.moves.append(Move(player, row, col))

    def computer_move(self, player) -> None:
        # Get the spaces with most real estate
        # Or Dumb

        # Naive version: literally just claim the first open square you see
        b = self._make_board() # Grid of moves

        for i, row in enumerate(b): # Rows

            for j, piece_2 in enumerate(row): # Cols

                if piece_2 == Piece.EMPTY:

                    self.moves.append(Move(player, i, j))
                    return
                    
        # ToDo:
        # Handler for if the board is already filled up
            


@app.command()

def main(
    player_1: Annotated[str, typer.Option(
        prompt="Player 1's Name (will play as X). Enter 'cpu' for computer player")],
    player_2: Annotated[str, typer.Option(
        prompt="Player 2's Name (will play as O). Enter 'cpu' for computer player")],
    board_size: Annotated[int, typer.Option(
        prompt="Board Side Length (Minimum of 3)", min=3)] = 3,
):

    # Woah, this works! 
    p1 = Player(player_1, Piece.X, player_1 in ("cpu"))
    p2 = Player(player_2, Piece.O, player_2 in ("cpu"))

    if player_1 in ("", "cpu"):
        p1 = Player(player_1, Piece.X, True)
    else:
        p1 = Player(player_1, Piece.X, False)

    if player_2 in ("", "cpu"):
        p2 = Player(player_2, Piece.O, True)
    else:
        p2 = Player(player_2, Piece.O, False)

    b = Board(board_size,[p1, p2])

    while b.check_game_status(b.current_player) == GameStatus.IN_PROGRESS:

        print(b, "\n")

        try:

            if b.current_player.is_computer:
                b.computer_move(b.current_player)
            else:

                position = typer.prompt(
                    f"Player {b.current_player.name}: Enter the (row col) to place your piece {b.current_player.piece} (use 1-based indexing)") 
                try:
                    row, col = map(int, position.split())
                except ValueError:
                    print(f"The (row, col) input didn't work. Enter two integer values separated by a space.")
                    continue

                b.move(b.current_player, row-1 , col-1)

            if b.check_game_status(b.current_player) == GameStatus.WIN:
                print(f"Player {b.current_player.name} WON!")
                print(b, "\n")
                return
            elif b.check_game_status(b.current_player) == GameStatus.DRAW:
                print("The game ended in a draw!")
                print(b, "\n")
                return

        except ValueError as e: 
            typer.echo(e)
            continue

        b.set_current_player()
        

if __name__ == "__main__":
    typer.echo("Tic Tac Toe!")
    app()
