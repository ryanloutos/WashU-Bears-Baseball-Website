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

def calcPitchWhiffRate(outing):
    pitches_swung_at = {"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0, "total":0}
    pitches_missed = {"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0, "total":0}
    pitches_whiff = {"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0, "total":0}

    for pitch in outing.pitches:
        if pitch.pitch_result == 'SS':
            pitches_swung_at[PitchType(pitch.pitch_type).name] += 1
            pitches_missed[PitchType(pitch.pitch_type).name] += 1
            pitches_swung_at['total'] += 1
            pitches_missed['total'] += 1
        if pitch.pitch_result == 'F' or pitch.pitch_result == 'IP':
            pitches_swung_at[PitchType(pitch.pitch_type).name] += 1
            pitches_swung_at['total'] += 1
    for key,val in pitches_swung_at.items():
        if (pitches_swung_at[key] != 0):
            pitches_whiff[key] = pitches_missed[key]/pitches_swung_at[key] * 100
    
    return (pitches_whiff)


def calcPitchStrikePercentage(outing):
    num_pitches = outing.pitches.count()
    pitches = {"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0, "total":0}
    pitches_strikes = {"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0, "total":0}

    for pitch in outing.pitches:
        pitches[PitchType(pitch.pitch_type).name] += 1
        pitches['total'] += 1
        if pitch.pitch_result == 'SS' or pitch.pitch_result == 'CS' or pitch.pitch_result == 'F' or pitch.pitch_result == 'IP':
            pitches_strikes[PitchType(pitch.pitch_type).name] += 1
            pitches_strikes['total'] += 1

    pitch_strike_percentage = {"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0, "total":0}
    for key,val in pitches.items():
        if pitches[key] != 0:
            pitch_strike_percentage[key] = pitches_strikes[key]/pitches[key] * 100

    return (pitch_strike_percentage)

def calcAverageVelo(outing):
    num_pitches = outing.pitches.count()
    pitches = {"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0}
    pitches_total_velo = {"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0}

    for pitch in outing.pitches:
        pitches[PitchType(pitch.pitch_type).name] += 1
        if (pitch.velocity):
            pitches_total_velo[PitchType(pitch.pitch_type).name] += pitch.velocity

    pitch_avg_velo = {"FB":0, "CB":0, "SL":0, "CH":0, "CT":0, "SM":0}
    for key,val in pitches.items():
        if pitches[key] != 0:
            pitch_avg_velo[key] = pitches_total_velo[key]/pitches[key]

    return (pitch_avg_velo)

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
    # With each value being 0<=val<=100

# calculate pitch usage by batter count
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
                counts_percentages[key]["pitches"][pitch] = value["pitches"][pitch]/total * 100
                counts_percentages[key]["total"] = total/num_pitches
        else:  # case in which there were no pitches thrown in a count
            counts_percentages[key]["pitches"] = counts[key]["pitches"]
            counts_percentages[key]["total"] = 0

    return (counts, counts_percentages)

    
