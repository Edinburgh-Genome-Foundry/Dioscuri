"""Classes for representing a Gemini WorkList (gwl).

The gwl file specification is based on the Freedom EVOware Software Manual,
393172, v3.5 (2015), for the Tecan Freedom EVOware v2.7 software (note
different versioning for manual and software).

A gwl file is made up of records. A record consists of a single character
indicating the operation type, and one or more 'parameters'.

DiTi is short for 'Disposable Tip'.
"""

# The magic character semicolon (;) appearing throughout the script is used as
# a separator and is specified by the gwl fileformat.


def read_gwl(filepath):
    worklist = GeminiWorkList()

    with open(filepath) as f:
        records_as_strings = f.read().splitlines()  # read txt lines
    for record_as_string in records_as_strings:
        entries = record_as_string.split(";")
        if entries[0] == "A" or entries[0] == "D":
            record = Pipette(
                operation=entries[0],
                rack_label=entries[1],
                rack_id=entries[2],
                rack_type=entries[3],
                position=entries[4],
                tube_id=entries[5],
                volume=entries[6],
                liquid_class=entries[7],
                # tip_type is entry #8
                tip_mask=entries[9],
                forced_rack_type=entries[10],
            )
        elif entries[0] == "W":
            record = WashTipOrReplaceDITI()
        elif entries[0] == "W1":
            record = WashTipOrReplaceDITI(scheme=1)
        elif entries[0] == "W2":
            record = WashTipOrReplaceDITI(scheme=2)
        elif entries[0] == "W3":
            record = WashTipOrReplaceDITI(scheme=3)
        elif entries[0] == "W4":
            record = WashTipOrReplaceDITI(scheme=4)
        elif entries[0] == "WD":
            record = Decontamination()
        elif entries[0] == "F":
            record = Flush()
        elif entries[0] == "B":
            record = Break()
        elif entries[0] == "S":
            record = SetDITIType(*entries[1:])  # first one is the record type
        elif entries[0] == "C":
            record = Comment(*entries[1:])
        elif entries[0] == "R":
            record = ReagentDistribution(*entries[1:])
        else:
            raise ValueError("Entry `%s` is not a valid record type." % entries[0])

        worklist.add_record(record)

    return worklist


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

        if type(record) is SetDITIType:
            if len(self.records) != 0:
                if type(self.records[-1]) != Break:
                    raise ValueError(
                        "The Set DiTi Type record can only be used at the very"
                        " beginning of the worklist or directly after a Break record."
                    )

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

        return records_as_string

    def records_to_file(self, filename):
        records_as_string = self.records_to_string()
        with open(filename, "w", encoding="utf8") as f:
            f.write(records_as_string)


class Pipette:
    """General class for Aspirate and Dispense records.

    Note that parameter MinDetectedVolume is not implemented.


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
        # Order is important:
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
    """The Flush record."""

    def __init__(self):
        self.type_character = "F"

    def to_string(self):
        """Convert record into string representation."""
        record_as_string = self.type_character + ";"

        return record_as_string


class Break:
    """The Break record."""

    def __init__(self):
        self.type_character = "B"

    def to_string(self):
        """Convert record into string representation."""
        record_as_string = self.type_character + ";"

        return record_as_string


class SetDITIType:
    """The Set DiTi Type record.

    The Set DiTi Type record can only be used at the very beginning of the worklist or
    directly after a Break record.


    **Parameters**

    **DiTi_Index**
    > The index of DiTi Type (`str`). Used to switch DiTi types from within a worklist.
    """

    def __init__(self, diti_index):
        self.diti_index = diti_index
        self.type_character = "S"

    def to_string(self):
        """Convert record into string representation."""
        parameters = [self.type_character, self.diti_index]
        record_as_string = ";".join(parameters)

        return record_as_string


class Comment:
    """The Comment record (ignored by Freedom EVOware).

    **Parameters**

    **comment**
    > The comment (`str`). Newlines (`\\n`) will be escaped with `\`.
    """

    def __init__(self, comment):
        if "\n" in comment:
            self.comment = comment.replace("\n", "\\n")
        else:
            self.comment = comment
        self.type_character = "C"

    def to_string(self):
        """Convert record into string representation."""
        parameters = [self.type_character, self.comment]
        record_as_string = ";".join(parameters)

        return record_as_string


class ReagentDistribution:
    """The Reagent Distribution record.


    **Parameters**

    **SrcRackLabel**
    > Label (`str`) of source labware. Maximum 32 characters.

    **SrcRackID**
    > Source labware barcode (`str`). Maximum 32 characters.

    **SrcRackType**
    > Source labware type (`str`): configuration name. Maximum 32 characters.

    **SrcPosStart**
    > First well to be used in the source labware (`int`). Range: 1 .. number of wells.

    **SrcPosEnd**
    > Last well to be used in the source labware (`int`). Range: 1 .. number of wells.

    **DestRackLabel**
    > Label (`str`) of destination labware. Maximum 32 characters.

    **DestRackID**
    > Destination labware barcode (`str`). Maximum 32 characters.

    **DestRackType**
    > Destination labware type (`str`): configuration name. Maximum 32 characters.

    **DestPosStart**
    > First well to be used in the destination labware (`int`).
    > Range: 1 .. number of wells.

    **DestPosEnd**
    > Last well to be used in the destination labware (`int`).
    > Range: 1 .. number of wells.

    **Volume**
    > Dispense volume (`int`) in the destination labware in μl (microliter).
    > Range: 0..7158278.

    **LiquidClass**
    > Optional (`str`). Overwrites the liquid class specified in the Tecan
    EVOware Worklist command. Maximum 32 characters.

    **NoOfDitiReuses**
    > Optional (`int`). Maximum number of DiTi reuses allowed
    > (default 1 = no DiTi reuse).

    **NoOfMultiDisp**
    > Optional (`int`). Maximum number of dispenses in a multidispense sequence
    > (default 1 = no multi-dispense).

    **Direction**
    > Optional (`int`). Pipetting direction
    > (0 = left to right, 1 = right to left; default = 0).

    **ExcludeDestWell**
    > Optional (`str`). List of wells in destination labware to be excluded from
    > pipetting.
    """

    def __init__(
        self,
        SrcRackLabel,
        SrcRackID,
        SrcRackType,
        SrcPosStart,
        SrcPosEnd,
        DestRackLabel,
        DestRackID,
        DestRackType,
        DestPosStart,
        DestPosEnd,
        Volume,
        LiquidClass="",
        NoOfDitiReuses=1,
        NoOfMultiDisp=1,
        Direction=0,
        ExcludeDestWell="",
    ):
        self.type_character = "R"

        self.SrcRackLabel = SrcRackLabel
        self.SrcRackID = SrcRackID
        self.SrcRackType = SrcRackType
        self.SrcPosStart = str(SrcPosStart)
        self.SrcPosEnd = str(SrcPosEnd)
        self.DestRackLabel = DestRackLabel
        self.DestRackID = DestRackID
        self.DestRackType = DestRackType
        self.DestPosStart = str(DestPosStart)
        self.DestPosEnd = str(DestPosEnd)
        self.Volume = str(Volume)
        self.LiquidClass = LiquidClass
        self.NoOfDitiReuses = str(NoOfDitiReuses)
        self.NoOfMultiDisp = str(NoOfMultiDisp)
        self.Direction = str(Direction)
        self.ExcludeDestWell = ExcludeDestWell

    def to_string(self):
        # Order is important:
        parameters = [
            self.type_character,
            self.SrcRackLabel,
            self.SrcRackID,
            self.SrcRackType,
            self.SrcPosStart,
            self.SrcPosEnd,
            self.DestRackLabel,
            self.DestRackID,
            self.DestRackType,
            self.DestPosStart,
            self.DestPosEnd,
            self.Volume,
            self.LiquidClass,
            self.NoOfDitiReuses,
            self.NoOfMultiDisp,
            self.Direction,
            self.ExcludeDestWell,
        ]
        record_as_string = ";".join(parameters)

        return record_as_string
