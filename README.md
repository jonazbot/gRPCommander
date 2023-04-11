# gRPCommander
gRPCommander is a commandline tool for simplifying sending gRPC commands and receiving responses
to a service I am working on. It is built as a wrapper around gRPCurl and requires JSON files to be tailored for the 
service to configure the gRPC commands.

## Content
- [Run gRPCommander](#run-grpcommander) 
- [Utility commands](#utility-commands) 
  - [ls](#ls)
  - [Default](#default)
  - [Load](#load)
  - [Quit](#quit)
- [gRPC commands](#grpc-commands)
  - [AddSite](#addsite)
  - [RemoveSite](#removesite)
  - [GetSite](#getsite)
  - [AddSockets](#addsockets)
  - [UpdateSockets](#updatesockets)
  - [RemoveSockets](#removesockets)
  - [GetSockets](#getsockets)

## Run gRPCommander
To run gRPCommander open a terminal and navigate to the project root directory. 
```shell
cd grpc-commands && python3 gRPCommander.py
```

## Utility commands

### ls
List all JSON files loaded by gRPCommander.
```
ls
```

List the contents of a loaded site.
```
ls [site]
```

*Note: All files in `grpc-commands/` with prefix `AddSite-` and postfix `.json` are loaded at startup by default.*

### Default
Set a default site from the list of loaded sites
```
Default [site]
```

*Note: Set a site as the default site at startup to use implied site commands*

### Load
Load a site from file. 
```
Load [file]... 
```

### Quit
Stop gRPCommander
```
Quit
```


## gRPC commands
The `[site]` property can be omitted when sending commands to the default site. 
See the [Default](#default) command to set a default site.    

### AddSite
Send an `AddSite` gRPC command to add a loaded site.
```
AddSite [site]
```

### RemoveSite
Send a `RemoveSite` gRPC command to remove all site sockets.
```
RemoveSite [site]
```

### GetSite
Send a `GetSite` gRPC query.
```
GetSite [site]
```

### AddSockets
Send an `AddSockets` gRPC command to add sockets to a site.
```
AddSocket [site] [socket]...
```

### UpdateSockets
Send a `UpdateSockets` gRPC command.
```
UpdateSockets [site] [Socket]...
```
*Note: `UpdateSockets` generates a new `topic` and a randomized `wss`.*

### RemoveSockets
Send a `RemoveSockets` gRPC command.
```
RemoveSockets [site] [SocketName]...
```

### GetSockets
Send a `GetSockets` gRPC query.
```
GetSockets [site] [Socket]...
```
