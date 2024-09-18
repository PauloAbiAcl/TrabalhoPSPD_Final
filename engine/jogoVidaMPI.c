#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>
#include <mpi.h>
#include <time.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <string.h>

#define ind2d(i, j) ((i) * (tam + 2) + (j))

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

// Função para enviar dados ao Elasticsearch (sem modificações)
void enviar_dados_para_elasticsearch(const char* engine_name, int tam, double tempo_init, double tempo_comp, double tempo_fim, double tempo_total) {
    char curl_cmd[1024];
    const char* elasticsearch_url = "http://elasticsearch:9200/tempo_mpi_engine/_doc/";

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

// Função que retorna o tempo atual (sem modificações)
double wall_time(void) {
    struct timeval tv;
    struct timezone tz;

    gettimeofday(&tv, &tz);
    return (tv.tv_sec + tv.tv_usec / 1000000.0);
}

// Função principal do Jogo da Vida (sem modificações)
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

void extrair_valores_json(const char *json_str, int *powmin, int *powmax) {
    char *powmin_str = strstr(json_str, "\"powmin\":");
    char *powmax_str = strstr(json_str, "\"powmax\":");

    if (powmin_str != NULL && powmax_str != NULL) {
        // Avança o ponteiro para pegar o valor após "powmin":
        powmin_str += strlen("\"powmin\":");
        *powmin = atoi(powmin_str);

        // Avança o ponteiro para pegar o valor após "powmax":
        powmax_str += strlen("\"powmax\":");
        *powmax = atoi(powmax_str);
    } else {
        printf("Erro: Não foi possível encontrar 'powmin' ou 'powmax' no JSON.\n");
        *powmin = -1;
        *powmax = -1;
    }
}

void receber_numeros_via_socket(int *powmin, int *powmax) {
    int server_fd, client_socket;
    struct sockaddr_in server_addr;
    int opt = 1;
    int addrlen = sizeof(server_addr);
    char buffer[1024] = {0};

    // Cria o socket
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("Erro ao criar o socket");
        exit(EXIT_FAILURE);
    }

    // Configura o socket
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt))) {
        perror("Erro ao configurar o socket");
        exit(EXIT_FAILURE);
    }

    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(8081);

    // Faz o bind do socket
    if (bind(server_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("Erro no bind");
        exit(EXIT_FAILURE);
    }

    // Espera por conexões
    if (listen(server_fd, 3) < 0) {
        perror("Erro no listen");
        exit(EXIT_FAILURE);
    }

    printf("Esperando por conexão...\n");

    // Aceita uma conexão
    if ((client_socket = accept(server_fd, (struct sockaddr *)&server_addr, (socklen_t*)&addrlen)) < 0) {
        perror("Erro ao aceitar conexão");
        exit(EXIT_FAILURE);
    }

    // Lê os dados do cliente
    read(client_socket, buffer, 1024);

    // Extrai valores "powmin" e "powmax" do JSON manualmente
    extrair_valores_json(buffer, powmin, powmax);

    if (*powmin != -1 && *powmax != -1) {
        printf("Recebido POWMIN: %d, POWMAX: %d\n", *powmin, *powmax);
    }

    close(client_socket);
    close(server_fd);
}

// Função principal do programa (modificada para usar o socket)
int main(int argc, char *argv[]) {
    int pow;
    int i, tam, *tabulIn, *tabulOut;
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

    // Receber os valores POWMIN e POWMAX via socket
    int POWMIN, POWMAX;
    if (rank == 0) {
        receber_numeros_via_socket(&POWMIN, &POWMAX);
        MPI_Send(&POWMIN, 1, MPI_INT, 1, 0, MPI_COMM_WORLD);
        MPI_Send(&POWMAX, 1, MPI_INT, 1, 0, MPI_COMM_WORLD);
    } else {
        MPI_Recv(&POWMIN, 1, MPI_INT, 0, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        MPI_Recv(&POWMAX, 1, MPI_INT, 0, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
    }

    // Para todos os tamanhos do tabuleiro
    for (pow = POWMIN; pow <= POWMAX; pow++) {
        tam = 1 << pow;

        int tam_por_processo = tam / 2;
        int first = (rank == 0) ? 1 : tam_por_processo + 1;
        int last = (rank == 0) ? tam_por_processo : tam;

        t0 = wall_time();
        tabulIn = (int *)malloc((tam + 2) * (tam + 2) * sizeof(int));
        tabulOut = (int *)malloc((tam + 2) * (tam + 2) * sizeof(int));
        InitTabul(tabulIn, tabulOut, tam);
        t1 = wall_time();

        for (i = 0; i < 2 * (tam - 3); i++) {
            UmaVida(tabulIn, tabulOut, tam);
            UmaVida(tabulOut, tabulIn, tam);
        }

        MPI_Barrier(MPI_COMM_WORLD);
        t2 = wall_time();

        if (rank == 0) {
            int resultado_correto = Correto(tabulIn, tam);
            printf("%d\n", resultado_correto);
            if (resultado_correto)
                printf("**RESULTADO CORRETO**\n");
            else
                printf("**RESULTADO ERRADO**\n");
        }

        MPI_Barrier(MPI_COMM_WORLD);
        t3 = wall_time();

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
