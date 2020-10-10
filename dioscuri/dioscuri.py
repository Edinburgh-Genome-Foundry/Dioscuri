"""Classes for representing a Gemini WorkList (gwl).

The gwl file specification is based on the Freedom EVOware Software Manual,
393172, v3.5 (2015), for the Tecan Freedom EVOware v2.7 software (note
different versioning for manual and software).

DiTi is short for 'Disposable Tip'.
"""

# The magic character semicolon (;) appearing throughout the script is used as
# a separator and is specified by the gwl fileformat.


class GeminiWorkList:
    """Gemini WorkList (gwl) class.

    A WorkList is a list of pipetting commands, or 'records'.


    **Parameters**

    **name**
    > name of the worklist (`str`).

    **records**
    > `list` of records (Pipette class instances).
    """

    def __init__(self, name="worklist", records=None):
        self.name = name
        if records is None:
            self.records = []
        else:
            self.records = records

    def add_record(self, record):
        """Add record.


        **Parameters**

        **record**
        > `Pipette`
        """
        if not type(record) in [
            Pipette,
            WashTipOrReplaceDITI,
            Decontamination,
            Flush,
            Break,
            SetDITIType,
            Comment,
            ReagentDistribution,
        ]:
            raise AssertionError("Parameter `record` must be a record class.")
        self.records.append(record)

    def list_records(self):
        record_list = []
        for record in self.records:
            record_list.append(record.type_character)
        return record_list

    def records_to_string(self):
        records_as_string = ""
        for record in self.records:
            records_as_string += record.to_string()
            records_as_string += "\n"
            pass

        return records_as_string


class Pipette:
    """General class for Aspirate and Dispense records.

    A record consists of a single character indicating the operation type, and
    one or more 'parameters'. Note that parameter MinDetectedVolume is not
    implemented.


    **Parameters**

    **operation**
    > The type of the transfer (`str`): `A` for aspirate, or `D` for dispense.
    > The first letter of the specified string is used.

    **rack_label**
    > Label (`str`) which is assigned to the labware. Maximum 32 characters.

    **rack_id**
    > Labware barcode (`str`). Maximum 32 characters.

    **rack_type**
    > Labware type (`str`): configuration name, for example "384 Well,
    landscape". Maximum 32 characters.

    **position**
    > Well position in the labware (`int`). The position starts with 1 and
    increases from rear to front and left to right. Range: 1 .. number of wells.

    **tube_id**
    > Tube barcode (`str`). Maximum 32 characters.

    **volume**
    > Pipetting volume (`int`) in µl (microliter). Range: 0 .. 7158278.

    **liquid_class**
    > Optional (`str`). Overwrites the liquid class specified in the Tecan
    EVOware Worklist command that calls the gwl file. Maximum 32 characters.

    **tip_mask**
    > Optional (`str`). Specifies the tip you want to use. See details in the
    program that uses the gwl output file. Range: 1 .. 128.

    **forced_rack_type**
    > Optional (`str`). The configuration name of the labware.
    Maximum 32 characters.
    """

    def __init__(
        self,
        operation,
        rack_label,
        rack_type,
        position,
        volume,
        tube_id="",
        rack_id="",
        liquid_class="",
        tip_mask="",
        forced_rack_type="",
    ):

        if not operation[0] in ["A", "D"]:
            raise ValueError("Parameter `operation` must be one of 'A' or 'D'.")
        else:
            self.type_character = operation[0]

        # Parameters:
        self.rack_label = rack_label
        self.rack_id = rack_id
        self.rack_type = rack_type
        self.position = position
        self.tube_id = tube_id
        self.volume = volume
        self.liquid_class = liquid_class
        self.tip_mask = tip_mask
        self.forced_rack_type = forced_rack_type

        self.tip_type = ""  # Reserved, must be omitted.

    def to_string(self):
        parameters = [
            self.type_character,
            self.rack_label,
            self.rack_id,
            self.rack_type,
            str(self.position),
            self.tube_id,
            str(self.volume),
            self.liquid_class,
            self.tip_type,
            self.tip_mask,
            self.forced_rack_type,
        ]
        record_as_string = ";".join(parameters)

        return record_as_string


class WashTipOrReplaceDITI:
    """Class for WashTip or ReplaceDITI records.


    **Parameters**

    **scheme**
    > Number (`int`) of wash scheme to use. Default `None`, which uses the
    first wash scheme.
    """

    def __init__(self, scheme=None):
        if scheme is None:
            self.scheme = ""
        else:
            if scheme not in [1, 2, 3, 4]:
                raise ValueError("Scheme must be between 1 and 4.")
            self.scheme = str(scheme)

        self.type_character = "W"

    def to_string(self):
        """Convert record into string representation."""
        record_as_string = self.type_character + self.scheme + ";"

        return record_as_string


class Decontamination:
    """The Decontamination Wash record."""

    def __init__(self):
        self.type_character = "WD"

    def to_string(self):
        """Convert record into string representation."""
        record_as_string = self.type_character + ";"

        return record_as_string


class Flush:
    pass


class Break:
    pass


class SetDITIType:
    pass


class Comment:
    pass


class ReagentDistribution:
    pass
