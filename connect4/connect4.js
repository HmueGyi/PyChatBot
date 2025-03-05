var playerRed = "R";
var playerYellow = "Y";
var currPlayer = playerYellow; // Change the starting player to the computer (Yellow)

var gameOver = false;
var board;

var rows = 6;
var columns = 7;
var currColumns = []; // Keeps track of which row each column is at.

window.onload = function() {
    setGame();
    if (currPlayer === playerYellow) {
        setTimeout(computerMove, 500); // Make the computer move right after the game starts
    }
}

function setGame() {
    board = [];
    currColumns = [5, 5, 5, 5, 5, 5, 5]; // Reset column heights

    // Get the board element
    const boardElement = document.getElementById("board");
    boardElement.innerHTML = ''; // Clear previous tiles

    // Initialize the turn indicator
    document.getElementById("turn-indicator").innerText = "Your Turn"; // Your starts first

    // Create new tiles and add event listeners
    for (let r = 0; r < rows; r++) {
        let row = [];
        for (let c = 0; c < columns; c++) {
            row.push(' ');
            let tile = document.createElement("div");
            tile.id = r.toString() + "-" + c.toString();
            tile.classList.add("tile");
            tile.addEventListener("click", playerMove); // Bind playerMove event
            boardElement.appendChild(tile);
        }
        board.push(row);
    }
}

function createBoard() {
    // Get the board element and clear any existing tiles
    const boardElement = document.getElementById("board");
    boardElement.innerHTML = ''; // Clear the board

    // Re-create the tiles and add event listeners for player moves
    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < columns; c++) {
            let tile = document.createElement("div");
            tile.id = r.toString() + "-" + c.toString(); // Unique ID for each tile
            tile.classList.add("tile"); // Add the "tile" class
            tile.classList.remove("red-piece", "yellow-piece"); // Remove old piece classes
            tile.addEventListener("click", playerMove); // Reattach event listener for player moves
            boardElement.appendChild(tile); // Add tile to the board
        }
    }
}


function playerMove() {
    if (gameOver || currPlayer !== playerRed) {
        return;
    }

    let coords = this.id.split("-");
    let c = parseInt(coords[1]);
    let r = currColumns[c];

    if (r < 0) {
        return;
    }

    placePiece(r, c, playerRed);
    if (!gameOver) {
        setTimeout(computerMove, 500); // Delay to simulate computer thinking
    }
}

function computerMove() {
    if (gameOver) return;

    let availableColumns = currColumns.map((val, index) => (val >= 0 ? index : null)).filter(val => val !== null);

    if (availableColumns.length === 0) return;

    // 1. Check if the bot can win in the next move
    for (let c of availableColumns) {
        let r = currColumns[c];
        if (r >= 0) {
            board[r][c] = playerYellow;
            if (checkPotentialWin(playerYellow)) {
                placePiece(r, c, playerYellow);
                return;
            }
            board[r][c] = ' ';
        }
    }

    // 2. Check if the player is about to win and block it
    for (let c of availableColumns) {
        let r = currColumns[c];
        if (r >= 0) {
            board[r][c] = playerRed;
            if (checkPotentialWin(playerRed)) {
                board[r][c] = ' '; // Reset test move
                placePiece(r, c, playerYellow);
                return;
            }
            board[r][c] = ' ';
        }
    }

    // 3. Prefer the center column for better positioning
    let centerColumn = Math.floor(columns / 2);
    if (availableColumns.includes(centerColumn)) {
        let r = currColumns[centerColumn];
        placePiece(r, centerColumn, playerYellow);
        return;
    }

    // 4. Otherwise, play a random move
    let c = availableColumns[Math.floor(Math.random() * availableColumns.length)];
    let r = currColumns[c];
    placePiece(r, c, playerYellow);
}

function checkPotentialWin(player) {
    // Simulate checkWinner logic to determine if the current board state results in a win
    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < columns - 3; c++) {
            if (board[r][c] === player && board[r][c+1] === player && board[r][c+2] === player && board[r][c+3] === player) {
                return true;
            }
        }
    }

    for (let c = 0; c < columns; c++) {
        for (let r = 0; r < rows - 3; r++) {
            if (board[r][c] === player && board[r+1][c] === player && board[r+2][c] === player && board[r+3][c] === player) {
                return true;
            }
        }
    }

    for (let r = 0; r < rows - 3; r++) {
        for (let c = 0; c < columns - 3; c++) {
            if (board[r][c] === player && board[r+1][c+1] === player && board[r+2][c+2] === player && board[r+3][c+3] === player) {
                return true;
            }
        }
    }

    for (let r = 3; r < rows; r++) {
        for (let c = 0; c < columns - 3; c++) {
            if (board[r][c] === player && board[r-1][c+1] === player && board[r-2][c+2] === player && board[r-3][c+3] === player) {
                return true;
            }
        }
    }

    return false;
}

function dropPiece(r, c, player) {
    board[r][c] = player;
    let tile = document.getElementById(r.toString() + "-" + c.toString());
    tile.classList.add(player === playerRed ? "red-piece" : "yellow-piece");

    // Apply animation delay based on row position for a staggered effect
    let delay = (rows - r) * 100;
    tile.style.animationDelay = delay + "ms";

    currColumns[c] = r - 1;
    setTimeout(() => {
        checkWinner();
        checkDraw();
        currPlayer = (player === playerRed) ? playerYellow : playerRed;
    }, delay + 1000); // Wait for animation to complete before switching players
}

function placePiece(r, c, player) {
    board[r][c] = player;
    let tile = document.getElementById(r.toString() + "-" + c.toString());
    tile.classList.add(player === playerRed ? "red-piece" : "yellow-piece");
    
    currColumns[c] = r - 1;
    updateTurnIndicator(); // Update the turn message
    
    checkWinner();
    checkDraw();
    currPlayer = (player === playerRed) ? playerYellow : playerRed;
}

function updateTurnIndicator() {
    let turnIndicator = document.getElementById("turn-indicator");
    if (gameOver) {
        turnIndicator.innerText = "";
    } else {
        turnIndicator.innerText = currPlayer === playerRed ? "PyChatBot Turn" : "Your Turn";
    }
}


function checkWinner() {
    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < columns - 3; c++) {
            if (board[r][c] !== ' ' && board[r][c] === board[r][c+1] && board[r][c] === board[r][c+2] && board[r][c] === board[r][c+3]) {
                setWinner(r, c);
                return;
            }
        }
    }

    for (let c = 0; c < columns; c++) {
        for (let r = 0; r < rows - 3; r++) {
            if (board[r][c] !== ' ' && board[r][c] === board[r+1][c] && board[r][c] === board[r+2][c] && board[r][c] === board[r+3][c]) {
                setWinner(r, c);
                return;
            }
        }
    }

    for (let r = 0; r < rows - 3; r++) {
        for (let c = 0; c < columns - 3; c++) {
            if (board[r][c] !== ' ' && board[r][c] === board[r+1][c+1] && board[r][c] === board[r+2][c+2] && board[r][c] === board[r+3][c+3]) {
                setWinner(r, c);
                return;
            }
        }
    }

    for (let r = 3; r < rows; r++) {
        for (let c = 0; c < columns - 3; c++) {
            if (board[r][c] !== ' ' && board[r][c] === board[r-1][c+1] && board[r][c] === board[r-2][c+2] && board[r][c] === board[r-3][c+3]) {
                setWinner(r, c);
                return;
            }
        }
    }
}

function checkDraw() {
    let availableColumns = currColumns.filter(c => c >= 0);
    if (availableColumns.length === 0 && !gameOver) {
        let winner = document.getElementById("winner");
        winner.innerText = "It's a Draw!";
        gameOver = true;
    }
}

function setWinner(r, c) {
    let winner = document.getElementById("winner");
    let turnIndicator = document.getElementById("turn-indicator");

    if (board[r][c] === playerRed) {
        // winner.innerText = "Red Wins!";
        turnIndicator.innerText = "PyChatBot : You win! You may be lucky this time.";
    } else {
        // winner.innerText = "Yellow Wins!";
        turnIndicator.innerText = "PyChatBot : I Wins! You know this game is so easy";
    }

    gameOver = true;
}

function resetGame() {
    gameOver = false;
    currPlayer = playerYellow; // Restart with the computer
    board = [];
    currColumns = [5, 5, 5, 5, 5, 5, 5]; // Reset column heights

    // Reset the board visually
    setGame();
    if (currPlayer === playerYellow) {
        setTimeout(computerMove, 500); // Make the computer move right after the game starts
    }
    // Show the initial turn indicator
    document.getElementById("turn-indicator").innerText = "Your Turn"; // Show Your's turn at reset
}