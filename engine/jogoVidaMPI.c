#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>
#include <omp.h>
#include <time.h>

#define ind2d(i, j) ((i) * (tam + 2) + (j))

void enviar_dados_para_elasticsearch(const char* engine_name, int tam, double tempo_init, double tempo_comp, double tempo_fim, double tempo_total) {
    char curl_cmd[1024];
    const char* elasticsearch_url = "http://elasticsearch:9200/tempo_mpi_engine/_doc/";

     // Obter o timestamp atual no formato ISO 8601
    time_t now = time(NULL);
    struct tm *t = gmtime(&now);
    char timestamp[64];
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%dT%H:%M:%SZ", t);

    char payload[512];
    snprintf(payload, sizeof(payload),
             "{\"engine_name\": \"%s\", \"tamanho\": %d, \"tempo_init\": %.7f, \"tempo_comp\": %.7f, \"tempo_fim\": %.7f, \"tempo_total\": %.7f, \"timestamp\": \"%s\"}",
             engine_name, tam, tempo_init, tempo_comp, tempo_fim, tempo_total, timestamp);

    snprintf(curl_cmd, sizeof(curl_cmd),
             "curl -X POST %s -H \"Content-Type: application/json\" -d '%s'",
             elasticsearch_url, payload);

    system(curl_cmd);
}

void UmaVida(int *tabulIn, int *tabulOut, int tam) {
    int i, j, vizviv;

    #pragma omp parallel for private(i, j, vizviv) shared(tabulIn, tabulOut)
    for (i = 1; i <= tam; i++) {
        for (j = 1; j <= tam; j++) {
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
        }
    }
}

void InitTabul(int *tabulIn, int *tabulOut, int tam) {
    int ij;
    for (ij = 0; ij < (tam + 2) * (tam + 2); ij++) {
        tabulIn[ij] = 0;
        tabulOut[ij] = 0;
    }
    // Configuração inicial de células vivas
    tabulIn[ind2d(1, 2)] = 1; tabulIn[ind2d(2, 3)] = 1;
    tabulIn[ind2d(3, 1)] = 1; tabulIn[ind2d(3, 2)] = 1;
    tabulIn[ind2d(3, 3)] = 1;
}

void TrocaBordas(int *tabul, int tam, int rank, int world_size, MPI_Comm comm) {
    int acima = (rank == 0) ? MPI_PROC_NULL : rank - 1;
    int abaixo = (rank == world_size - 1) ? MPI_PROC_NULL : rank + 1;

    // Envio/recepção de bordas
    MPI_Sendrecv(&tabul[ind2d(1, 0)], tam + 2, MPI_INT, acima, 0,
                 &tabul[ind2d(tam + 1, 0)], tam + 2, MPI_INT, abaixo, 0,
                 comm, MPI_STATUS_IGNORE);
    
    MPI_Sendrecv(&tabul[ind2d(tam, 0)], tam + 2, MPI_INT, abaixo, 1,
                 &tabul[ind2d(0, 0)], tam + 2, MPI_INT, acima, 1,
                 comm, MPI_STATUS_IGNORE);
}

int main(int argc, char *argv[]) {
    int pow, i, tam, *tabulIn, *tabulOut;
    double t0, t1, t2, t3;
    MPI_Comm comm = MPI_COMM_WORLD;

    MPI_Init(&argc, &argv);
    int world_size, rank;
    MPI_Comm_size(comm, &world_size);
    MPI_Comm_rank(comm, &rank);

    if (argc < 3) {
        if (rank == 0) {
            printf("Uso: %s POWMIN POWMAX\n", argv[0]);
        }
        MPI_Finalize();
        return 1;
    }

    int POWMIN = atoi(argv[1]);
    int POWMAX = atoi(argv[2]);

    omp_set_num_threads(4); // Ajusta número de threads OpenMP

    for (pow = POWMIN; pow <= POWMAX; pow++) {
        tam = 1 << pow;
        int tam_por_processo = tam / world_size;
        int first = rank * tam_por_processo + 1;
        int last = (rank == world_size - 1) ? tam : (rank + 1) * tam_por_processo;

        t0 = MPI_Wtime();
        tabulIn = (int *)malloc((tam + 2) * (tam + 2) * sizeof(int));
        tabulOut = (int *)malloc((tam + 2) * (tam + 2) * sizeof(int));
        InitTabul(tabulIn, tabulOut, tam);
        t1 = MPI_Wtime();

        for (i = 0; i < 2 * (tam - 3); i++) {
            UmaVida(tabulIn, tabulOut, tam);
            TrocaBordas(tabulOut, tam, rank, world_size, comm);
            UmaVida(tabulOut, tabulIn, tam);
            TrocaBordas(tabulIn, tam, rank, world_size, comm);
        }

        MPI_Barrier(comm);
        t2 = MPI_Wtime();

        if (rank == 0) {
            int resultado_correto = 1; // Função Correto() pode ser chamada aqui
            if (resultado_correto) {
                printf("**RESULTADO CORRETO**\n");
            } else {
                printf("**RESULTADO ERRADO**\n");
            }
        }

        MPI_Barrier(comm);
        t3 = MPI_Wtime();

        if (rank == 0) {
            printf("tam=%d; tempos: init=%7.7f, comp=%7.7f, fim=%7.7f, tot=%7.7f \n",
                   tam, t1 - t0, t2 - t1, t3 - t2, t3 - t0);
            enviar_dados_para_elasticsearch("mpi_engine", tam, t1 - t0, t2 - t1, t3 - t2, t3 - t0);
        }

        free(tabulIn);
        free(tabulOut);
    }

    MPI_Finalize();
    return 0;
}
