/*
 * Test-only MySQL 5.7 loadable UDF for the independent Pebbles lab.
 * This source is never copied into the published target image.
 * Compile against Ubuntu 16.04 / MySQL 5.7 headers to retain the old ABI.
 */
#include <mysql/mysql.h>
#include <stdlib.h>
#include <string.h>

my_bool ttp_exec_init(UDF_INIT *initid, UDF_ARGS *args, char *message)
{
    (void)initid;
    if (args->arg_count != 1) {
        strcpy(message, "ttp_exec requires one command argument");
        return 1;
    }
    args->arg_type[0] = STRING_RESULT;
    return 0;
}

long long ttp_exec(UDF_INIT *initid, UDF_ARGS *args, char *is_null, char *error)
{
    (void)initid;
    if (args->args[0] == NULL) {
        *is_null = 1;
        return 0;
    }
    const size_t length = (size_t)args->lengths[0];
    char *command = (char *)malloc(length + 1);
    if (!command) {
        *error = 1;
        return -1;
    }
    memcpy(command, args->args[0], length);
    command[length] = '\0';
    int status = system(command);
    free(command);
    return (long long)status;
}
