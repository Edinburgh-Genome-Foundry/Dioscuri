"""Classes for representing a Gemini WorkList (gwl).

The gwl file specification is based on the Freedom EVOware Software Manual,
393172, v3.5 (2015), for the Tecan Freedom EVOware v2.7 software (note
different versioning for manual and software).

DiTi is short for 'Disposable Tip'.
"""


class GeminiWorkList:
    """Gemini WorkList (gwl) class.

    A WorkList is a list of pipetting commands, or 'records'.


    Parameters
    ==========

    name
      str name of the worklist.

    records
      list of records (Pipette class instances).
    """

    def __init__(self, name="worklist", records=None):
        self.name = name
        if records is None:
            self.records = []
        else:
            self.records = records

    def add_record(self, record):
        self.records.append(record)

    def list_records(self):
        for record in self.records:
            # call readable print of record
            pass

    def records_to_string(self):
        records_as_string = ""
        for record in self.records:
            records_as_string += record.to_string()
            records_as_string += "\n"
            pass

        return records_as_string


class Pipette:
    """General class for Aspirate and Dispense records.

    A record consists of a single character indicating the type, and one or
    more 'parameters'. Note that parameter MinDetectedVolume is not implemented.


    Parameters
    ==========

    type
      str the type of the transfer: 'A' for aspirate, or 'D' for dispense.

    rack_label
      str label (name) which is assigned to the labware. Maximum 32 characters.

    rack_id
      str labware barcode. Maximum 32 characters.

    rack_type
      str labware type (configuration name), for example "384 Well, landscape".
      Maximum 32 characters.

    position
      int well position in the labware. The position starts with 1 and increases
      from rear to front and left to right. Range: 1 .. number of wells.

    tube_id
      str tube barcode. Maximum 32 characters.

    volume
      int pipetting volume in µl (microliter). Range: 0 .. +7158278.

    liquid_class
      str. Optional. Overwrites the liquid class specified in the Tecan EVOware
      Worklist command that calls the gwl file. Maximum 32 characters.

    tip_mask
      str. Optional. Specifies the tip you want to use. See details in the
      program that uses the gwl output file. Range: 1 .. 128.

    forced_rack_type
      str. Optional. The configuration name of the labware.
      Maximum 32 characters.
    """

    def __init__(
        self,
        type,
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

        self.type_character = type[0]

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


    Parameters
    ==========

    scheme
      int number of wash scheme to use. Default None, which uses the first
      wash scheme.
    """

    def __init__(self, scheme=None):
        if scheme is None:
            self.scheme = ""
        else:
            self.scheme = str(scheme)

        self.type_character = "W"

    def to_string(self):
        record_as_string = self.type_character + self.scheme + ";"

        return record_as_string


class Decontamination:
    pass


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
