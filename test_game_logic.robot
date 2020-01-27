*** Settings ***
Documentation     Game Logic test cases of Find Pairs memory card game.

Library           Collections
Library           String
Library           GameLogicTestLibrary.py

*** Variables ***
@{board1}    1a    1b    2a    2b    3a    3b    4a    4b    5a    5b
@{turns1}    0    1    2    3    4    5    6    7    8    9
@{expected_score1}    3    2

@{board2}    1a    1b    2a    2b    3a    3b    4a    4b    5a    5b    6a    6b    7a    7b    8a    8b    9a    9b    10a    10b
@{turns2}    0    1    2    3    4    5    6    7    8    9    10    11    12    13    14    15    16    17    18    19
@{expected_score2}    4    3    3

@{board3}    1a    1b    2a    2b    3a    3b    4a    4b    5a    5b    6a    6b    7a    7b    8a    8b    9a    9b    10a    10b
@{turns3}    0    1    2    4    2    3    4    5    6    7    8    9    10    11    12    13    14    15    16    17    18    19
@{expected_score3}    4    3    3


*** Test Cases ***     numPlayers    numPairs           user     board        turns        expected_score
Game Initialization    [Template]    Initialize Game
                       2             5                  Veera
                       3             10                 Helmi

Playing                [Template]    Play Game
                       2             5                  Veera    ${board1}    ${turns1}    ${expected_score1}
                       3             10                 Helmi    ${board2}    ${turns2}    ${expected_score2}
                       3             10                 Helmi    ${board3}    ${turns3}    ${expected_score3}

*** Keywords ***
Initialize Game
    [Arguments]    ${numPlayers}    ${numPairs}    ${user}
    Init database    ${numPlayers}    ${numPairs}    ${user}
    Print match
    Check game initialization

Turn One Card
    [Arguments]    ${turn}    ${board}    ${cards_faceup}
    ${playerInTurn}=    Get player in turn
    ${position}=        Convert To Integer    ${turn}
    ${faceValue}=       Get Substring    ${board}[${position}]    0    -1    # remove the letter a/b
    &{faceup}=          Create Dictionary    position=${position}    faceValue=${faceValue}
    Turn card                 ${playerInTurn}    ${position}
    Append To List            ${cards_faceup}    ${faceup}
    Faceup Cards Should Be    ${cards_faceup}

Do Turns
    [Arguments]    ${turns}    ${board}
    @{faceups}=    Create List
    FOR    ${turn}    IN    @{turns}
        Turn One Card    ${turn}    ${board}    ${faceups}
        ${faceups}=    Check if should clear faceups    ${faceups}
    END

Play Game
    [Arguments]    ${numPlayers}    ${numPairs}    ${user}    ${board}    ${turns}    ${expected_score}

    Initialize Game    ${numPlayers}    ${numPairs}    ${user}
    Mock board         ${board}
    Do Turns           ${turns}    ${board}
    Score should be    ${expected_score}
