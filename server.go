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



func initGame(conn net.Conn) (board [][]bool, e error) {
    // first, we read the board stats request
    // START X Y M Q (we assume 128 bytes is enough---for now!
    readBuff := make([]byte, 128)
    _, readErr := conn.Read(readBuff)
    if readErr != nil {
        return nil, fmt.Errorf("Error in initial read: ", readErr)
    }
    
    // convert our bytes into a string.
    str := string(readBuff)

    // parse the string, we expect <INT> <INT> <INT> Q,
    // where Q is just a delimiter to make our lives easier.
    // Lots of error checking here!
    start_strings := strings.Split(str, " ")
    if len(start_strings) != 5 {
        return nil, fmt.Errorf("Poorly formatted initial query: ", str)
    }
    if start_strings[0] != "START" {
        fmt.Println("Error: first string not START, is actually: ", start_strings[0])
        return nil, fmt.Errorf("Poorly formatted initial query")
    }

    // ok, we have at least the right number of fields, now we parse each in turn
    // PARSE X
    x, readErr := strconv.Atoi(start_strings[1])
    if readErr != nil {
        return nil, fmt.Errorf("Error parsing x with error: ", readErr)
    }
    if !(0 < x && x < 256) { // magic number will be replaced by static board field
        return nil, fmt.Errorf("Error, x is invalid value", x)
    }

    // PARSE Y
    y, readErr := strconv.Atoi(start_strings[2])
    if readErr != nil {
        return nil, fmt.Errorf("Error parsing y with error: ", readErr)
    }
    if !(0 < x && x < 256) { // magic number will be replaced by static board field
        return nil, fmt.Errorf("Error, y is invalid value", y)
    }


    // PARSE M
    m, readErr := strconv.Atoi(start_strings[3])
    if readErr != nil {
        return nil, fmt.Errorf("Error parsing m with error: ", readErr)
    }
    if !(0 < x && x < x*y) { // magic number will be replaced by static board field
        return nil, fmt.Errorf("Error, m is invalid value", m)
    }

    written, writeErr := conn.Write([]byte("MADE"))
    if written != 4 {
        return nil, fmt.Errorf("Error, did not manage to write all 4 bytes of \"MADE\", assuming connection problem")
    }
    if writeErr != nil {
        return nil, fmt.Errorf("Error on writing \"MADE\"", writeErr)
    }

    // probably return error value here, too?
    board = initBoard(x,y,m)
    return board, nil
}

// this should handle a lot more errors, soon
func parseQuery(str string) (x, y int, err error) {
        coords := strings.Split(str, " ")
        x, err = strconv.Atoi(coords[0])
        y, err = strconv.Atoi(coords[1])
        return
}

// query format: "<X> <Y> Q", where <X> and <Y> are ints
// eg: 5 3 Q
// the Q is just a terminal to make parsing easier.
func handleConnection(conn net.Conn) {
    fmt.Println("New connection initialized")
    board, initErr := initGame(conn)
    if initErr != nil {
        fmt.Println(initErr)
        return
    }
    printBoard(board)

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

        x, y, _ := parseQuery(str)
        
        res := strconv.Itoa(queryBoard(board,x,y))
        //res_as_bytes := []byte(res)
        conn.Write([]byte(res))
    }
}

func main() {
    ln, err := net.Listen("tcp", ":8080")
    if err != nil {
        // handle error
    }
    for {
        // we get a new connection
        conn, err := ln.Accept()
        if err != nil {
            // handle error
        }
        
        go handleConnection(conn)
    }
}
