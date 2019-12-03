from app import db
from enum import Enum

# enum for tranlating pitch types into categories easier
class PitchType(Enum):
    FB = 1
    CB = 2
    SL = 3
    CH = 4
    CT = 5
    SM = 7


# Caculate the percentage of each pitch thrown
def calcPitchPercentages(outing):
    num_pitches = outing.pitches.count()
    pitches = {"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0}

    for pitch in outing.pitches:
        pitches[PitchType(pitch.pitch_type).name] += 1

    pitch_percentages = {"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0}
    for key,val in pitches.items():
        pitch_percentages[key] = pitches[key]/num_pitches * 100

    return (pitches, pitch_percentages)
    # Will be in form {"FB":0.0, "CB":0.0, "SL":0.0, "CH":0.0, "CT":0.0, "SM":0.0}
    # Wit each value being 0<=val<=100

# calculate 
def pitchUsageByCount(outing):
    num_pitches = outing.pitches.count()
    # PLEASE COLLAPSE THIS VARIABLE IT'S DUMB
    counts = {
        "0-0":{
            "pitches":{"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0},
            "total":0
            },
        "0-1":{
            "pitches":{"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0},
            "total":0
            },
        "0-2":{
            "pitches":{"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0},
            "total":0
            },
        "1-0":{
            "pitches":{"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0},
            "total":0
            },
        "1-1":{
            "pitches":{"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0},
            "total":0
            },
        "1-2":{
            "pitches":{"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0},
            "total":0
            },
        "2-0":{
            "pitches":{"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0},
            "total":0
            },
        "2-1":{
            "pitches":{"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0},
            "total":0
            },
        "2-2":{
            "pitches":{"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0},
            "total":0
            },
        "3-0":{
            "pitches":{"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0},
            "total":0
            },
        "3-1":{
            "pitches":{"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0},
            "total":0
            },
        "3-2":{
            "pitches":{"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0},
            "total":0
            }
    }
    counts_percentages = {
        "0-0":{
            "pitches":{"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0},
            "total":0
            },
        "0-1":{
            "pitches":{"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0},
            "total":0
            },
        "0-2":{
            "pitches":{"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0},
            "total":0
            },
        "1-0":{
            "pitches":{"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0},
            "total":0
            },
        "1-1":{
            "pitches":{"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0},
            "total":0
            },
        "1-2":{
            "pitches":{"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0},
            "total":0
            },
        "2-0":{
            "pitches":{"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0},
            "total":0
            },
        "2-1":{
            "pitches":{"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0},
            "total":0
            },
        "2-2":{
            "pitches":{"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0},
            "total":0
            },
        "3-0":{
            "pitches":{"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0},
            "total":0
            },
        "3-1":{
            "pitches":{"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0},
            "total":0
            },
        "3-2":{
            "pitches":{"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0},
            "total":0
            }
    }
    for pitch in outing.pitches:
        count = f"{pitch.count_balls}-{pitch.count_strikes}"  # gives something like 0-0
        pitch_type = PitchType(pitch.pitch_type).name

        counts[count]["total"] += 1
        counts[count]["pitches"][pitch_type] += 1
    
    # create count percentages
    for key,value in counts.items():
        total = value["total"]
        if total != 0:
            for pitch in value["pitches"].keys():
                counts_percentages[key]["pitches"][pitch] = value["pitches"][pitch]/total
                counts_percentages[key]["total"] = total/num_pitches
        else:  # case in which there were no pitches thrown in a count
            counts_percentages[key]["pitches"] = counts[key]["pitches"]
            counts_percentages[key]["total"] = 0

    return (counts, counts_percentages)

