#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>
#include <mpi.h>

#define ind2d(i, j) ((i) * (tam + 2) + (j))
#define POWMIN 3
#define POWMAX 10

double wall_time(void) {
    struct timeval tv;
    struct timezone tz;

    gettimeofday(&tv, &tz);
    return (tv.tv_sec + tv.tv_usec / 1000000.0);
}

void UmaVida(int *tabulIn, int *tabulOut, int tam)
{
    int i, j, vizviv;

    #pragma omp parallel for private(i, j, vizviv) shared(tabulIn, tabulOut)
    for (i = 1; i <= tam; i++)
    {
        for (j = 1; j <= tam; j++)
        {
            vizviv = tabulIn[ind2d(i - 1, j - 1)] + tabulIn[ind2d(i - 1, j)] +
                     tabulIn[ind2d(i - 1, j + 1)] + tabulIn[ind2d(i, j - 1)] +
                     tabulIn[ind2d(i, j + 1)] + tabulIn[ind2d(i + 1, j - 1)] +
                     tabulIn[ind2d(i + 1, j)] + tabulIn[ind2d(i + 1, j + 1)];
            if (tabulIn[ind2d(i, j)] && vizviv < 2)
                tabulOut[ind2d(i, j)] = 0;
            else if (tabulIn[ind2d(i, j)] && vizviv > 3)
                tabulOut[ind2d(i, j)] = 0;
            else if (!tabulIn[ind2d(i, j)] && vizviv == 3)
                tabulOut[ind2d(i, j)] = 1;
            else
                tabulOut[ind2d(i, j)] = tabulIn[ind2d(i, j)];
        } /* fim-for */
    } /* fim-for */
} /* fim-UmaVida */

void DumpTabul(int *tabul, int tam, int first, int last, char *msg) {
    int i, ij;

    printf("%s; Dump posicoes [%d:%d, %d:%d] de tabuleiro %d x %d\n",
           msg, first, last, first, last, tam, tam);
    for (i = first; i <= last; i++) printf("="); printf("=\n");
    for (i = ind2d(first, 0); i <= ind2d(last, 0); i += ind2d(1, 0)) {
        for (ij = i + first; ij <= i + last; ij++)
            printf("%c", tabul[ij] ? 'X' : '.');
        printf("\n");
    }
    for (i = first; i <= last; i++) printf("="); printf("=\n");
}

void InitTabul(int *tabulIn, int *tabulOut, int tam) {
    int ij;

    for (ij = 0; ij < (tam + 2) * (tam + 2); ij++) {
        tabulIn[ij] = 0;
        tabulOut[ij] = 0;
    }

    tabulIn[ind2d(1, 2)] = 1; tabulIn[ind2d(2, 3)] = 1;
    tabulIn[ind2d(3, 1)] = 1; tabulIn[ind2d(3, 2)] = 1;
    tabulIn[ind2d(3, 3)] = 1;
}

int Correto(int *tabul, int tam) {
    int ij, cnt;

    cnt = 0;
    for (ij = 0; ij < (tam + 2) * (tam + 2); ij++)
        cnt = cnt + tabul[ij];
    return (cnt == 5 && tabul[ind2d(tam - 2, tam - 1)] &&
            tabul[ind2d(tam - 1, tam)] && tabul[ind2d(tam, tam - 2)] &&
            tabul[ind2d(tam, tam - 1)] && tabul[ind2d(tam, tam)]);
}

int main(int argc, char *argv[]) {
    int pow;
    int i, tam, *tabulIn, *tabulOut;
    char msg[9];
    double t0, t1, t2, t3;

    MPI_Init(&argc, &argv);
    int world_size, rank;
    MPI_Comm_size(MPI_COMM_WORLD, &world_size);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    if (world_size != 2) {
        if (rank == 0) {
            printf("Este programa requer exatamente 2 processos MPI.\n");
        }
        MPI_Finalize();
        return 1;
    }

    // Para todos os tamanhos do tabuleiro
    for (pow = POWMIN; pow <= POWMAX; pow++) {
        tam = 1 << pow;

        // Divide o tabuleiro igualmente entre os dois processos
        int tam_por_processo = tam / 2;
        int first = (rank == 0) ? 1 : tam_por_processo + 1;
        int last = (rank == 0) ? tam_por_processo : tam;

        // Aloca e inicializa tabuleiros
        t0 = wall_time();
        tabulIn = (int *)malloc((tam + 2) * (tam + 2) * sizeof(int));
        tabulOut = (int *)malloc((tam + 2) * (tam + 2) * sizeof(int));
        InitTabul(tabulIn, tabulOut, tam);
        t1 = wall_time();

        // Executa as iterações do jogo da vida
        for (i = 0; i < 2 * (tam - 3); i++) {
            UmaVida(tabulIn, tabulOut, tam);
            UmaVida(tabulOut, tabulIn, tam);
        }

        // Sincroniza os processos para garantir que ambos terminaram a computação
        MPI_Barrier(MPI_COMM_WORLD);
        t2 = wall_time();

        // Verifica se o resultado está correto (somente no processo 0)
        if (rank == 0) {
            int resultado_correto = Correto(tabulIn, tam);
            printf("%d\n", resultado_correto);
            if (resultado_correto)
                printf("**RESULTADO CORRETO**\n");
            else
                printf("**RESULTADO ERRADO**\n");
        }

        // Sincroniza os processos novamente antes de imprimir os tempos
        MPI_Barrier(MPI_COMM_WORLD);
        t3 = wall_time();

        // Imprime os tempos (somente no processo 0)
        if (rank == 0) {
            printf("tam=%d; tempos: init=%7.7f, comp=%7.7f, fim=%7.7f, tot=%7.7f \n",
                   tam, t1 - t0, t2 - t1, t3 - t2, t3 - t0);
        }

        free(tabulIn);
        free(tabulOut);
    }

    MPI_Finalize();
    return 0;
}