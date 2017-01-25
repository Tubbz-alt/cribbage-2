#include <stdio.h>
#include "cribbage_score.h"

int main(int argc, char *argv[])
{
    printf("Hello world!\n");

    printf("\n\n----------\nscore_hand\n----------\n\n");

    printf("Score %d should be 7\n", score_hand(5,19,43,28,35,0));
    printf("Score %d should be 0\n", score_hand(6,34,0,51,37,0));
    printf("Score %d should be 0\n", score_hand(21,45,29,10,22,0));
    printf("Score %d should be 5\n", score_hand(25,46,16,6,31,0));
    printf("Score %d should be 6\n", score_hand(31,33,25,12,43,0));
    printf("Score %d should be 6\n", score_hand(50,25,30,3,10,0));
    printf("Score %d should be 12\n", score_hand(43,17,37,41,50,0));
    printf("Score %d should be 9\n", score_hand(36,3,24,23,25,0)); // special jack
    printf("Score %d should be 14\n", score_hand(45,28,17,15,16,0)); // double run
    printf("Score %d should be 6\n", score_hand(29,1,37,27,40,0)); // double run

    printf("\n\n----------\nscore_play\n----------\n\n");

    printf("Score %d should be 0\n",
           score_play((play_list_t){22, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
                       0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}));
    printf("Score %d should be 2\n",
           score_play((play_list_t){22, 4, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
                       0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}));
    printf("Score %d should be 0\n",
           score_play((play_list_t){22, 4, 45, 0xFF, 0xFF, 0xFF, 0xFF,
                       0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}));
    printf("Score %d should be 3\n",
           score_play((play_list_t){22, 4, 45, 18, 0xFF, 0xFF, 0xFF,
                       0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}));
    printf("Score %d should be 0\n",
           score_play((play_list_t){31, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
                       0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}));
    printf("Score %d should be 0\n",
           score_play((play_list_t){31, 3, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
                       0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}));
    printf("Score %d should be 2\n",
           score_play((play_list_t){31, 3, 16, 0xFF, 0xFF, 0xFF, 0xFF,
                       0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}));
    printf("Score %d should be 0\n",
           score_play((play_list_t){45, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
                       0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}));
    printf("Score %d should be 2\n",
           score_play((play_list_t){45, 32, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
                       0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}));
    printf("Score %d should be 6\n",
           score_play((play_list_t){45, 32, 6, 0xFF, 0xFF, 0xFF, 0xFF,
                       0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}));
    printf("Score %d should be 0\n",
           score_play((play_list_t){45, 32, 6, 4, 0xFF, 0xFF, 0xFF,
                       0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}));
    printf("Score %d should be 2\n",
           score_play((play_list_t){45, 32, 6, 4, 43, 0xFF, 0xFF,
                       0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}));
    printf("Score %d should be 0\n",
           score_play((play_list_t){20, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
                       0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}));
    printf("Score %d should be 0\n",
           score_play((play_list_t){20, 9, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
                       0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}));
    printf("Score %d should be 2\n",
           score_play((play_list_t){20, 9, 22, 0xFF, 0xFF, 0xFF, 0xFF,
                       0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}));
    printf("Score %d should be 0\n",
           score_play((play_list_t){22, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
                       0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}));
    printf("Score %d should be 2\n",
           score_play((play_list_t){22, 4, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
                       0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}));
    printf("Score %d should be 0\n",
           score_play((play_list_t){22, 4, 45, 0xFF, 0xFF, 0xFF, 0xFF,
                       0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}));
    printf("Score %d should be 3\n",
           score_play((play_list_t){22, 4, 45, 18, 0xFF, 0xFF, 0xFF,
                       0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}));
    printf("Score %d should be 0\n",
           score_play((play_list_t){31, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
                       0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}));
    printf("Score %d should be 0\n",
           score_play((play_list_t){31, 3, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
                       0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}));
    printf("Score %d should be 2\n",
           score_play((play_list_t){31, 3, 16, 0xFF, 0xFF, 0xFF, 0xFF,
                       0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}));
    printf("Score %d should be 0\n",
           score_play((play_list_t){45, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
                       0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}));
    printf("Score %d should be 2\n",
           score_play((play_list_t){45, 32, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
                       0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}));
    printf("Score %d should be 6\n",
           score_play((play_list_t){45, 32, 6, 0xFF, 0xFF, 0xFF, 0xFF,
                       0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}));
    printf("Score %d should be 0\n",
           score_play((play_list_t){45, 32, 6, 4, 0xFF, 0xFF, 0xFF,
                       0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}));
    printf("Score %d should be 2\n",
           score_play((play_list_t){45, 32, 6, 4, 43, 0xFF, 0xFF,
                       0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}));
    printf("Score %d should be 0\n",
           score_play((play_list_t){20, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
                       0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}));
    printf("Score %d should be 0\n",
           score_play((play_list_t){20, 9, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
                       0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}));
    printf("Score %d should be 2\n",
           score_play((play_list_t){20, 9, 22, 0xFF, 0xFF, 0xFF, 0xFF,
                       0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}));

    return 0;
}
