---
layout: page
title: MySQL KPIs used in our implementation. 
parent: Supplementary Result
nav_order: 4
---

| Type | KPI |
|------|-----|
| Workload (43) | Current_QPS, MySQL.Connections_{Conn/Max_Used_Conn/Max_Conn}, MySQL.Questions, MySQL.Client_Thread_Activity_{Peak_Threads_-Connected/Peak_Threads_Running/Avg_Threads Running}, MySQL.Abor-ted_Connections_{attempts/timeouts}, MySQL.Slow_Queries, MySQL.Handlers, MySQL.Transaction_Handlers, Top_Command_Counters. |
| MySQL Memory (23) | MySQL.Thread_{Thread_Cache_Size/Threads_Cached/Threads_Created}, MySQL.Internal_Mem_{InnoDB_Buffer_Pool_Data/InnoDB_Log_Buffer-_Size/Additional_Mem_Pool_Size/InnoDB_Dictionary_Size/Key_Buffer-_Size/Query_Cache_Size/Ada_Hash_Index_Size/TokuDB_Cache_Size}, MySQL.Query_Cache_{Free_Mem/Query_Cache_Size/Hits/Inserts/Not-_Cached/Prunes/Queries_in_Cache/}, MySQL.Table_Open_Cache_Status_-{Openings/Hits/Misses/Misses_Due_to_Overflow/Table_Open-_Cache_Hit_Ratio}. |
| MySQL Internals (28) | MySQL.File_Openings, MySQL.Open_Files_{Open_Files/Open_Files_Limit/InnoDB_Open_Files}, MySQL.Open_Tables_{Open_Tables/Table_Open-_Cache}, MySQL.Temporary_Objects_Created_Tmp_{Tables/DIsk_Tables/Files}, MySQL.Select_Types_{Full_Join/Full_Range_Join/Range/Scan/Range_Check}, MySQL.Sorts_{Rows/Range/Merge_Passes/Scan}, MySQL.Table_Definition_Cache_{Open_Table_Definitions/Table_Definitions_Cache_Size/Opened_Table_Definitions}, MySQL.Table_Locks_{immediate/waited}, MySQL.Network_Traffic_{Inbound/Outbound}, MySQL.Network_Usage_Hourly_{Received/Sent}, MySQL.Query_Duration. |
| Node Resources (18) | Node.IO_Activity_{Page_In/Page_Our}, Node.Memory_Distribution_{Free/Total}, Node.CPU_Usage_{_Load/_Load_Max_Core_Utilization}, Node.Network_Traffic_{Inbound/Outbound}, Node.Swap_Activity_{In-Reads/Out_Writes}, Node.Disk_Latency. |
