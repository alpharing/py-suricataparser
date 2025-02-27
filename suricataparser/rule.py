from typing import Any, Optional, List


class Option:
    CLASSTYPE = "classtype"
    GID = "gid"
    METADATA = "metadata"
    REFERENCE = "reference"
    MSG = "msg"
    REV = "rev"
    SID = "sid"

    def __init__(self, name: str, value: Optional[Any] = None):
        self.name: str = name
        self.value: Optional[str, 'Metadata'] = value
        self.value: Optional[str, 'Reference'] = value

    def __eq__(self, other: 'Option') -> bool:
        return self.name == other.name and self.value == other.value

    def __str__(self) -> str:
        if not self.value:
            return "{name};".format(name=self.name)
        return "{name}:{value};".format(name=self.name, value=self.value)


class Metadata:
    def __init__(self, data: list):
        self.data = data

    def __str__(self) -> str:
        return ", ".join(self.data)

    def add_meta(self, name: str, value: str) -> list:
        self.data.append("{name} {value}".format(name=name, value=value))
        return self.data

    def pop_meta(self, name: str) -> list:
        meta_items = []
        metadata = []
        for meta in self.data:
            if meta.startswith(name):
                meta_items.append(meta)
            else:
                metadata.append(meta)
        self.data = metadata
        return meta_items


class Reference:
    def __init__(self, data: list):
        self.data = data

    def __str__(self) -> str:
        return ", ".join(self.data)

    def add_ref(self, name: str, value: str) -> list:
        self.data.append("{name} {value}".format(name=name, value=value))
        return self.data

    def pop_ref(self, name: str) -> list:
        ref_items = []
        reference = []
        for ref in self.data:
            if ref.startswith(name):
                ref_items.append(ref)
            else:
                reference.append(ref)
        self.data = reference
        return ref_items


class Rule:
    def __init__(self, enabled: bool, action: str, header: str,
                 options: List[Option], raw: Optional[str] = None):
        self.enabled = enabled
        self._action = action
        self._header = header
        self._options = options
        self._sid = None
        self._gid = None
        self._msg = None
        self._rev = None
        self._classtype = None
        self._metadata = []
        self._reference = []
        self._raw = raw
        if raw:
            self.build_options()
        else:
            self.build_rule()

    def __str__(self) -> str:
        return "{enabled}{rule}".format(enabled="" if self.enabled else "# ",
                                        rule=self.raw)

    @property
    def action(self) -> str:
        return self._action

    @property
    def classtype(self) -> str:
        return self._classtype

    @property
    def header(self) -> str:
        return self._header

    @property
    def metadata(self) -> list:
        return self._metadata

    @property
    def reference(self) -> list:
        return self._reference

    @property
    def msg(self) -> str:
        return self._msg

    @property
    def options(self) -> List[Option]:
        return self._options

    @property
    def raw(self) -> str:
        return self._raw

    @property
    def rev(self) -> Optional[int]:
        return self._rev

    @property
    def sid(self) -> Optional[int]:
        return self._sid

    def build_options(self):
        self._metadata = []
        for option in self._options:
            if option.name == Option.MSG:
                self._msg = option.value.strip('"')
            elif option.name == Option.SID:
                self._sid = int(option.value)
            elif option.name == Option.GID:
                self._gid = int(option.value)
            elif option.name == Option.REV:
                self._rev = int(option.value)
            elif option.name == Option.CLASSTYPE:
                self._classtype = option.value
            elif option.name == Option.METADATA:
                self._metadata.extend(option.value.data)
            elif option.name == Option.REFERENCE:
                self._reference.extend(option.value.data)

    def build_rule(self) -> str:
        self._raw = self._action + " " + self._header + " "
        self._raw += "({options})".format(options=" ".join([str(opt) for opt in self._options]))
        self.build_options()
        return self._raw

    def add_option(self, name: str, value: Optional[str] = None, index: Optional[int] = None):
        option = Option(name=name, value=value)
        if index is None:
            self._options.append(option)
        else:
            self._options.insert(index, option)
        self.build_rule()

    def pop_option(self, name: str):
        chosen_options = []
        options = []
        for opt in self._options:
            if opt.name != name:
                options.append(opt)
            else:
                chosen_options.append(opt)
        self._options = options
        self.build_rule()
        return chosen_options

    def get_option(self, name: str) -> List[Option]:
        return [option for option in self.options if option.name == name]

    def to_dict(self) -> dict:
        options = []
        for option in self.options:
            if option.name != Option.METADATA or option.name != Option.REFERENCE:
                options.append({"name": option.name, "value": option.value})
            else:
                options.append({"name": option.name, "value": option.value.data})

        return {
            "enabled": self.enabled, "action": self.action,
            "header": self.header, "options": options
        }
