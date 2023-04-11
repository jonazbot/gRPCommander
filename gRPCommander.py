#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import subprocess
import random
import string


class Jason:
    """
    Jason, the trusty side-kick of GRPCommander. Jason provides JSON generation
    """
    def __init__(self,
                 provider: str,
                 heritage: str,
                 server: str,
                 api: str,
                 sink: str,
                 websocket_address_length: int,
                 params: dict):
        self.provider = provider
        self.heritage = heritage
        self.server = server
        self.api = api
        self.sink = sink
        self.wss_length = websocket_address_length
        self.params = params

    @staticmethod
    def _find_sockets(site: str, socket_names: list[str], sites: dict[str: list[json]]) -> list[json]:
        """
        Find a socket in the dictionary
        :param site: The name of the site the socket belongs to
        :param socket_names: The name of the socket
        :param sites: The dictionary containing each loaded site as a dictionary
        :return: The list of sockets found in the dictionary or an empty list.
        """
        sockets: list[json] = list()
        if site in sites:
            for socketName in socket_names:
                for socket in sites.get(site):
                    if socketName == socket["name"]:
                        sockets.append(socket)
        return sockets

    def _generate_socket(self, site_name: str, socket_name: str) -> json:
        """
        Generate a json with a new `topic` and a randomized `wss`
        :param site_name: The name of the site the socket belongs to
        :param socket_name: The name of the socket
        :return: A json with the following key-value pairs: `name: str`, `topic: str`, `wss: str`
        """
        return {
            "name": f"{socket_name}",
            "topic": f"{site_name}.{self.provider}.{self.heritage}.{socket_name}",
            "wss": f"wss://{self.server}/{self.api}/{self.sink}/{self.generate(self.wss_length)}"
                   f"/channel?{'&'.join([f'{key}={self.params.get(key)}' for key in self.params])}"
        }

    @staticmethod
    def add_site(site: str, sites: dict[str: list[json]]) -> json:
        """
        Generate a json for the `AddSite` gRPC command
        :param site: The name of the site the socket belongs to
        :param sites: The dictionary of sites
        :return: A JSON with the following key-value pairs: `site: str`, `sockets: list[json]`
        """
        return json.dumps(
            {
                "site": f"{site}",
                "unitConversion": sites.get(site)[1]
            })

    def add_sockets(self, site: str, sockets: list[str], sites: dict[str: list[json]]) -> json:
        """
        Generate a json for the `AddSockets` gRPC command
        :param site: The name of the site to add to
        :param sockets: The name of the sockets to add
        :param sites: The dictionary of sites
        :return: A JSON with the following key-value pairs: `site: str`, `sockets: list[json]`
        """
        return json.dumps(
            {
                "site": f"{site}",
                "sockets": self._find_sockets(site=site, socket_names=sockets, sites=sites)
            })

    @staticmethod
    def remove_site(site: str) -> json:
        """
        Generate a JSON for the `RemoveSite` gRPC command
        :param site: The name of the site the socket belongs to
        :return: A JSON with the following key-value pair: `site: str`
        """
        return json.dumps(
            {
                'site': f'{site}'
            })

    @staticmethod
    def remove_sockets(site: str, socket_names: list[str]) -> json:
        """
        Generate a JSON for the `RemoveSockets` gRPC command
        :param site: The name of the site the socket belongs to
        :param socket_names: The name of the socket
        :return: A JSON with the following key-value pairs: `site: str`, `socketNames: str`
        """
        return json.dumps(
            {
                'site': f'{site}',
                'socketNames': socket_names
            })

    def update_sockets(self, site: str, sockets: list[str]) -> json:
        """
        Generate a JSON for the `UpdateSockets` gRPC command with a new `topic` and randomized `wss`
        :param site: The name of the site the socket belongs to
        :param sockets: The name of the socket
        :return: A JSON with the following key-value pairs: `site: str`, `sockets: str`
        """
        return json.dumps(
            {
                'site': f'{site}',
                "sockets":
                    [
                        self._generate_socket(site_name=site, socket_name=socket) for socket in sockets
                    ]
            })

    @staticmethod
    def get_site(site: str) -> json:
        """
        Generate a JSON for the `GetSite` gRPC command
        :param site: The name of the site the socket belongs to
        :return: A JSON with the following key-value pair: `site: str`
        """
        return json.dumps(
            {
                "site": f"{site}",
            })

    @staticmethod
    def get_sockets(site: str, socket_names: list[str]) -> json:
        """
        Generate a JSON for the `GetSockets` gRPC command
        :param site: The name of the site the sockets belong to
        :param socket_names: The names of the sockets to get
        :return: A JSON with the following key-value pairs: `site: str`, `socket: str`
        """
        return json.dumps(
            {
                "site": f"{site}",
                "socketNames": socket_names
            })

    @staticmethod
    def generate(n: int):
        return ''.join(random.choices(string.ascii_letters, k=n))


class GRPCommander:
    """
    GRPCommander, the gRPC testing hero.
    """

    def __init__(self, url: str, port: str, service: str, actor: str, jason: Jason, default_site: str = None):
        self.server = url
        self.port = port
        self.service = service
        self.actor = actor
        self.jason = jason
        self.sites: dict[str: list] = dict()
        self._load_all_sites()
        self.default_site = default_site

    def start(self) -> None:
        """
        Run gRPCommander
        """
        stop = False
        while not stop:
            command = input('\nEnter command: ').split(' ')
            stop = self._command_handler(command)

    def _command_handler(self, command: list[str]) -> bool:
        """
        Parse user commands
        :param command: The input from the user to be parsed as a command
        :return: True if the command is to quit, False otherwise
        """
        payload: json = None
        method = command.pop(0).lower()

        # gRPC commands
        if method == 'addsite':
            method = 'AddSite'
            if self.default_site is not None and len(command) == 0:
                payload = self.jason.add_site(site=self.default_site, sites=self.sites)
            elif len(command) == 1 and command[0] in self.sites:
                payload = self.jason.add_site(site=command[0], sites=self.sites)
        elif method == 'addsockets':
            method = 'AddSockets'
            if self.default_site is not None and len(command) > 0:
                payload = self.jason.add_sockets(site=self.default_site, sockets=command, sites=self.sites)
            elif len(command) > 1 and command[0] in self.sites and command[1] != '':
                payload = self.jason.add_sockets(site=command.pop(0), sockets=command, sites=self.sites)
        elif method == 'removesite':
            method = 'RemoveSite'
            if self.default_site is not None and len(command) == 0:
                payload = self.jason.remove_site(site=self.default_site)
            elif len(command) == 1 and command[0] != '':
                payload = self.jason.remove_site(site=command[0])
        elif method == 'removesockets':
            method = 'RemoveSockets'
            if self.default_site is not None and len(command) > 0 and command[0] not in self.sites:
                payload = self.jason.remove_sockets(site=self.default_site, socket_names=command)
            elif len(command) > 1 and command[0] in self.sites:
                payload = self.jason.remove_sockets(site=command.pop(0), socket_names=command)
        elif method == 'updatesockets':
            method = 'UpdateSockets'
            if self.default_site is not None and len(command) > 0:
                payload = self.jason.update_sockets(site=self.default_site, sockets=command)
            elif len(command) > 1 and command[0] != '':
                payload = self.jason.update_sockets(site=command.pop(0), sockets=command)
        elif method == 'getsite':
            method = 'GetSite'
            if self.default_site is not None and len(command) == 0:
                payload = self.jason.get_site(site=self.default_site)
            elif len(command) == 1 and command[0] != '':
                payload = self.jason.get_site(site=command[0])
        elif method == 'getsockets':
            method = 'GetSockets'
            if len(command) > 1 and command[0] != '' and command[0] != self.default_site and command[1] != '':
                payload = self.jason.get_sockets(site=command.pop(0), socket_names=command)
            elif self.default_site is not None and len(command) > 0:
                payload = self.jason.get_sockets(site=self.default_site, socket_names=command)

        # Util commands
        elif method == 'ls':
            if len(command) == 0:
                print(f'Sites:')
                [print(f'    {site}') for site in self.sites.keys()]
                return False
            elif len(command) == 1 and command[0] in self.sites:
                print(f'Site: {command[0]}\nSockets:')
                [print(json.dumps(socket, indent=4)) for socket in self.sites.get(command[0])]
                return False
        elif method == 'default' and len(command) == 1:
            self._set_default_site(command[0])
            return False
        elif method == 'load' and len(command) > 0:
            for site in command:
                self._add_site(self._load_site(site))
            return False
        elif method == 'q' or method == 'Quit' or method == 'Exit':
            print('Stopping gRPCommander...')
            return True
        else:
            print(f'Command {method} not recognized.')

        # Execute command
        if payload is None:
            print(f'Property {command} not recognized.')
        else:
            # Send gRPC
            self._run_grpc_command(method=method, payload=payload)
        return False

    def _load_all_sites(self) -> None:
        """
        Load all files with prefix "AddSite" and postfix ".json"
        """
        for file in os.listdir():
            if file.startswith("AddSite") and file.endswith(".json"):
                self._add_site(self._load_site(file))

    @staticmethod
    def _load_site(file: str) -> json:
        """
        Load an AddSite.json and add it to sites
        :return: the name of the loaded site
        """
        site = None
        try:
            with open(file, 'r') as site_json:
                site = json.load(site_json)
        except OSError:
            print(f'Failed to load site from {file}.')
        return site

    def _add_site(self, site: json) -> None:
        """
        Add a site to the sites dictionary
        """
        if site is not None:
            self.sites[site["site"]] = (site["sockets"], site["unitConversion"])
            print(f'Loaded {site["site"]}')

    def _set_default_site(self, site: str) -> bool:
        """
        Set the default site to enable shorthand commands
        :param site: The name of the site that should be the new default site
        :return: True if successful, False otherwise
        """
        if site in self.sites:
            self.default_site = site
            print(f'Default site set to {site}')
            return True
        else:
            print(f'Site {site} not found!')
            return False

    def _run_grpc_command(self, method: str, payload: json) -> None:
        """
        Run a gRPC command using `gRPCurl` in a local shell
        :param method: The type of the call
        :param payload: The JSON payload to send
        """
        cmd = f"grpcurl -d '{payload}' -plaintext {self.server}:{self.port} {self.service}.{self.actor}.{method}"
        print(f'$ {cmd}')
        subprocess.Popen(cmd, shell=True).communicate()


if __name__ == '__main__':
    GRPCommander(
        url='127.0.0.1',
        port='8888',
        service='',
        actor='',
        default_site='',
        jason=Jason(
            provider='',
            heritage='Great.Grand.Parent',
            server='',
            api='',
            sink='streamsets',
            websocket_address_length=159,
            params={
                'includeInitialValues': 'true',
                'heartbeatRate': '10',
                'searchFullHierarchy': 'true'})).start()

