#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <time.h>
#include <signal.h>
#include <netdb.h> // For NI_MAXHOST
#include <ifaddrs.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include "bacnet/bacdef.h"
#include "bacnet/config.h"
#include "bacnet/bactext.h"
#include "bacnet/basic/binding/address.h"
#include "bacnet/basic/sys/mstimer.h"
#include "bacnet/basic/services.h"
#include "bacnet/basic/tsm/tsm.h"
#include "bacnet/datalink/dlenv.h"
#include "bacnet/basic/object/device.h"
#include "bacnet/basic/object/ai.h"
#include "bacnet/basic/object/ao.h"
#include "bacnet/basic/object/av.h"
#include "bacnet/basic/object/bi.h"
#include "bacnet/basic/object/bo.h"
#include "bacnet/basic/object/bv.h"
#include "bacnet/datalink/bip.h"
#include "bacnet/basic/sys/debug.h"
#include "bacnet/basic/services.h"
#include "bacnet/npdu.h"
#include "bacnet/apdu.h"
#include "bacnet/basic/tsm/tsm.h"
#include "bacnet/datalink/datalink.h"
#include "bacnet/dcc.h"

/* Configuration structure */
typedef struct
{
    uint32_t device_id;
    char device_name[64];
    char ip_address[16];
    uint16_t port;
    uint32_t analog_inputs;
    uint32_t analog_outputs;
    uint32_t analog_values;
    uint32_t binary_inputs;
    uint32_t binary_outputs;
    uint32_t binary_values;
} BACnet_Config;

/* Global variables */
static BACnet_Config g_config;
static bool Device_Initialized = false;
static BACNET_CHARACTER_STRING My_Object_Name;
static volatile bool Running = true;

/* Signal handler for graceful shutdown */
static void handle_signal(int signo)
{
    (void)signo;
    Running = false;
}

/* Network diagnostics function */
static void print_network_interfaces(void)
{
    struct ifaddrs *ifap, *ifa;
    char host[NI_MAXHOST];

    printf("\nDetailed Network Interface Configuration:\n");
    printf("----------------------------------------\n");

    if (getifaddrs(&ifap) == -1)
    {
        perror("getifaddrs failed");
        return;
    }

    for (ifa = ifap; ifa != NULL; ifa = ifa->ifa_next)
    {
        if (ifa->ifa_addr == NULL)
            continue;

        if (ifa->ifa_addr->sa_family == AF_INET)
        {
            struct sockaddr_in *sa = (struct sockaddr_in *)ifa->ifa_addr;
            char *ip_str = inet_ntoa(sa->sin_addr);
            printf("Interface: %-8s  IP: %s\n", ifa->ifa_name, ip_str);

            /* Check if this interface matches our configured IP */
            if (strcmp(ip_str, g_config.ip_address) == 0)
            {
                printf("*** This interface matches configured BACnet IP ***\n");
            }
        }
    }

    freeifaddrs(ifap);
    printf("----------------------------------------\n");
}

/* Read configuration from INI file */
static int read_config(const char *filename)
{
    FILE *file = fopen(filename, "r");
    if (!file)
    {
        fprintf(stderr, "Failed to open config file: %s\n", filename);
        return -1;
    }

    char line[256];
    char key[64];
    char value[192];
    bool has_required_fields = false;

    /* Initialize config with defaults */
    memset(&g_config, 0, sizeof(BACnet_Config));
    g_config.port = 47808; // Default BACnet port

    printf("\nReading configuration from %s:\n", filename);
    printf("----------------------------------------\n");

    while (fgets(line, sizeof(line), file))
    {
        if (line[0] == '#' || line[0] == ';' || line[0] == '\n')
            continue;

        if (sscanf(line, "%63[^=]=%191[^\n]", key, value) == 2)
        {
            char *k = strchr(key, ' ');
            if (k)
                *k = '\0';

            /* Remove leading/trailing whitespace from value */
            char *v = value;
            while (*v == ' ')
                v++;
            char *end = v + strlen(v) - 1;
            while (end > v && *end == ' ')
                end--;
            *(end + 1) = '\0';

            printf("Reading: %s = %s\n", key, v);

            if (strcmp(key, "device_id") == 0)
            {
                g_config.device_id = atoi(v);
                has_required_fields = true;
            }
            else if (strcmp(key, "device_name") == 0)
                strncpy(g_config.device_name, v, sizeof(g_config.device_name) - 1);
            else if (strcmp(key, "ip_address") == 0)
                strncpy(g_config.ip_address, v, sizeof(g_config.ip_address) - 1);
            else if (strcmp(key, "port") == 0)
                g_config.port = atoi(v);
            else if (strcmp(key, "analog_inputs") == 0)
                g_config.analog_inputs = atoi(v);
            else if (strcmp(key, "analog_outputs") == 0)
                g_config.analog_outputs = atoi(v);
            else if (strcmp(key, "analog_values") == 0)
                g_config.analog_values = atoi(v);
            else if (strcmp(key, "binary_inputs") == 0)
                g_config.binary_inputs = atoi(v);
            else if (strcmp(key, "binary_outputs") == 0)
                g_config.binary_outputs = atoi(v);
            else if (strcmp(key, "binary_values") == 0)
                g_config.binary_values = atoi(v);
            else
                printf("Warning: Unknown configuration key: %s\n", key);
        }
    }

    fclose(file);
    printf("----------------------------------------\n");

    if (!has_required_fields)
    {
        fprintf(stderr, "Error: Required configuration fields missing\n");
        return -1;
    }

    return 0;
}

/* Initialize BACnet objects based on configuration */
static bool init_objects(void)
{
    uint32_t i;
    bool success = true;

    printf("\nInitializing BACnet Objects:\n");
    printf("----------------------------------------\n");

    /* Initialize Device object */
    if (!Device_Initialized)
    {
        printf("Setting up Device ID: %u\n", g_config.device_id);
        Device_Set_Object_Instance_Number(g_config.device_id);
        Device_Init(NULL);
        Device_Initialized = true;
        characterstring_init_ansi(&My_Object_Name, g_config.device_name);
    }

    /* Initialize Analog Inputs */
    printf("Creating %u Analog Inputs\n", g_config.analog_inputs);
    for (i = 0; i < g_config.analog_inputs; i++)
    {
        if (!Analog_Input_Create(i))
        {
            fprintf(stderr, "Failed to create Analog Input %u\n", i);
            success = false;
            continue;
        }
        Analog_Input_Present_Value_Set(i, 0.0);
    }

    /* Initialize Analog Outputs */
    printf("Creating %u Analog Outputs\n", g_config.analog_outputs);
    for (i = 0; i < g_config.analog_outputs; i++)
    {
        if (!Analog_Output_Create(i))
        {
            fprintf(stderr, "Failed to create Analog Output %u\n", i);
            success = false;
            continue;
        }
        Analog_Output_Present_Value_Set(i, 0.0, BACNET_APPLICATION_TAG_REAL);
    }

    /* Initialize Analog Values */
    printf("Creating %u Analog Values\n", g_config.analog_values);
    for (i = 0; i < g_config.analog_values; i++)
    {
        if (!Analog_Value_Create(i))
        {
            fprintf(stderr, "Failed to create Analog Value %u\n", i);
            success = false;
            continue;
        }
        Analog_Value_Present_Value_Set(i, 0.0, BACNET_APPLICATION_TAG_REAL);
    }

    /* Initialize Binary Inputs */
    printf("Creating %u Binary Inputs\n", g_config.binary_inputs);
    for (i = 0; i < g_config.binary_inputs; i++)
    {
        if (!Binary_Input_Create(i))
        {
            fprintf(stderr, "Failed to create Binary Input %u\n", i);
            success = false;
            continue;
        }
        Binary_Input_Present_Value_Set(i, BINARY_INACTIVE);
    }

    /* Initialize Binary Outputs */
    printf("Creating %u Binary Outputs\n", g_config.binary_outputs);
    for (i = 0; i < g_config.binary_outputs; i++)
    {
        if (!Binary_Output_Create(i))
        {
            fprintf(stderr, "Failed to create Binary Output %u\n", i);
            success = false;
            continue;
        }
        Binary_Output_Present_Value_Set(i, BINARY_INACTIVE, BACNET_APPLICATION_TAG_ENUMERATED);
    }

    /* Initialize Binary Values */
    printf("Creating %u Binary Values\n", g_config.binary_values);
    for (i = 0; i < g_config.binary_values; i++)
    {
        if (!Binary_Value_Create(i))
        {
            fprintf(stderr, "Failed to create Binary Value %u\n", i);
            success = false;
            continue;
        }
        Binary_Value_Present_Value_Set(i, BINARY_INACTIVE);
    }

    printf("----------------------------------------\n");
    return success;
}

/* Set environment variables for network configuration */
static bool set_network_config(void)
{
    char env_port[32];
    bool success = true;

    printf("\nBACnet Network Configuration:\n");
    printf("----------------------------------------\n");
    printf("Configured IP: %s\n", g_config.ip_address);
    printf("Configured Port: %u\n", g_config.port);

    /* Print current network interfaces */
    print_network_interfaces();

    /* Set environment variables */
    snprintf(env_port, sizeof(env_port), "%u", g_config.port);
    if (setenv("BACNET_IP_PORT", env_port, 1) != 0)
    {
        fprintf(stderr, "Failed to set BACNET_IP_PORT environment variable\n");
        success = false;
    }

    if (setenv("BACNET_IFACE", g_config.ip_address, 1) != 0)
    {
        fprintf(stderr, "Failed to set BACNET_IFACE environment variable\n");
        success = false;
    }

    /* Verify IP address format */
    struct in_addr addr;
    if (inet_aton(g_config.ip_address, &addr) == 0)
    {
        fprintf(stderr, "Error: Invalid IP address format: %s\n", g_config.ip_address);
        success = false;
    }

    printf("----------------------------------------\n");
    return success;
}

/* Main application */
int main(int argc, char *argv[])
{
    BACNET_ADDRESS src = {0};
    uint16_t pdu_len = 0;
    unsigned timeout = 100;
    time_t last_seconds = 0;
    time_t current_seconds = 0;
    bool init_success = true;

    printf("\nBACnet Emulator Starting...\n");
    printf("===========================================\n");

    if (argc != 2)
    {
        printf("Usage: %s <config.ini>\n", argv[0]);
        return 1;
    }

    /* Read configuration */
    if (read_config(argv[1]) != 0)
    {
        fprintf(stderr, "Failed to read configuration\n");
        return 1;
    }

    /* Set network configuration */
    if (!set_network_config())
    {
        fprintf(stderr, "Failed to configure network\n");
        return 1;
    }

    /* Initialize BACnet */
    printf("\nInitializing BACnet Stack...\n");
    Device_Init(NULL);
    if (!Device_Initialized)
    {
        fprintf(stderr, "Failed to initialize BACnet device\n");
        return 1;
    }

    address_init();
    dlenv_init();

    /* Initialize objects */
    if (!init_objects())
    {
        fprintf(stderr, "Warning: Some objects failed to initialize\n");
        /* Continue running, but with warning */
    }

    /* Setup signal handler */
    signal(SIGINT, handle_signal);
    signal(SIGTERM, handle_signal);

    printf("\nBACnet Emulator Running!\n");
    printf("Device ID: %u\n", g_config.device_id);
    printf("Device Name: %s\n", g_config.device_name);
    printf("Listening on %s:%u\n", g_config.ip_address, g_config.port);
    printf("Press Ctrl+C to exit\n");
    printf("===========================================\n\n");

    /* Main loop */
    uint8_t Rx_Buf[MAX_APDU] = {0};

    while (Running)
    {
        /* Update current time */
        current_seconds = time(NULL);

        /* Handle periodic tasks every second */
        if (current_seconds != last_seconds)
        {
            last_seconds = current_seconds;
            dcc_timer_seconds(1);
            bvlc_maintenance_timer(1);
            handler_cov_timer_seconds(1);
            tsm_timer_milliseconds(1000);
        }

        /* Handle any BACnet messages */
        pdu_len = bip_receive(&src, &Rx_Buf[0], MAX_APDU, timeout);
        if (pdu_len)
        {
            npdu_handler(&src, &Rx_Buf[0], pdu_len);
        }

        /* Handle any BACnet timeouts */
        handler_cov_task();
        tsm_timer_milliseconds(100);
    }

    printf("\nShutting down BACnet Emulator...\n");
    return 0;
}