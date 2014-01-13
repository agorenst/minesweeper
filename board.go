package main

import (
    "fmt"
    "math/rand"
    "net"
    "strconv"
    "strings"
)

// given an x, y, and number of mines, return such a board
func initBoard(x, y, m int) (board [][]bool) {
    board = make([][]bool,y)
    for i := 0; i < y; i++ {
        board[i] = make([]bool,x)
    }

    // now initialize the mines
    // Needs to be smarter: pick coords from a random grab-bag.
    // otherwise may end up with slightly fewer slots.
    for i := 0; i < m; i++ {
        randx := rand.Intn(x)
        randy := rand.Intn(y)
        board[randy][randx] = true
    }

    return
}

func inBounds(board [][]bool, x, y int) (res bool) {
    if (x < 0 || y < 0) {
        return false
    }
    if (y < len(board)) {
        //fmt.Println("y is inbounds: ", y, len(board))
        if (x < len(board[y])) {
            //fmt.Println("x is inbounds: ", x, len(board[y]))
            return true
        }
    }
    return false
}

// maybe use the two return values?
func queryBoard(board [][]bool, x, y int) (minecount int) {

    minecount = 0

    if (!inBounds(board, x, y)) {
        return -2
    }
    if (board[y][x]) {
        return -1
    }

    for i := -1; i < 2; i++ {
        for j := -1; j < 2; j++ {
            qx := x + i
            qy := y + j
            if inBounds(board, qx, qy) {
                if board[qy][qx] && (i != 0 || j != 0) {
                    minecount++;
                }
            }
        }
    }

    return
}

func printBoard(board [][]bool) {
    for _, v := range board {
        for _, b := range v {
            if !b {
                fmt.Printf("[ ]")
            } else {
                fmt.Printf("[X]")
            }
        }
        fmt.Printf("\n")
    }
}


// query format: "<X> <Y> Q", where <X> and <Y> are ints
// eg: 5 3 Q
// the Q is just a terminal to make parsing easier.
func handleConnection(conn net.Conn, board [][]bool) {
    fmt.Println("About to handle connection")
    readBuff := make([]byte, 128)
    for {
        _, con_err := conn.Read(readBuff)
        if (con_err != nil) {
            return
        }
        str := string(readBuff)
        if (str == "DONE") {
            return
        }
        coords := strings.Split(str, " ")
        x, _ := strconv.Atoi(coords[0])
        y, _ := strconv.Atoi(coords[1])
        
        res := strconv.Itoa(queryBoard(board,x,y))
        //res_as_bytes := []byte(res)
        conn.Write([]byte(res))
    }
}

func main() {
    board := initBoard(15,10,20)
    printBoard(board)
    ln, err := net.Listen("tcp", ":8080")
    if err != nil {
        // handle error
    }
    for {
        conn, err := ln.Accept()
        if err != nil {
            // handle error
        }
        
        // concurrency!
        handleConnection(conn, board)
    }
}
