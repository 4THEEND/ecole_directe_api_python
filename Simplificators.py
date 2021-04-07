import locale

from .Exceptions import *


def moyennesAnalyse(raw_moyennes, periode):
    notes = raw_moyennes['data']['periodes']
    del notes[-1]
    total = []
    for a in notes:
        c = [
            (b['codeMatiere'], b['moyenne']) for b in a['ensembleMatieres']['disciplines']
            if b['codeSousMatiere'] == '' and b['moyenne'] != ''
        ]
        total.append(c)
    if periode is None:
        return total
    else:
        if 0 != int(periode) <= len(total):
            try:
                return [total[int(periode) - 1]]
            except:
                raise BadPeriode
        else:
            raise BadPeriode


def notesAnalyse(raw_notes, periode_notes=None, matiere=None, min_max_moy=False):
    periodes = list(set([a['codePeriode'] for a in raw_notes]))
    periodes.sort()

    locale.setlocale(locale.LC_ALL, 'french')
    lst_finale = []
    lst_matiere = [list(set([a['codeMatiere'] for a in raw_notes if a['codePeriode'] == b])) for b in periodes]
    for periode in range(len(lst_matiere)):
        lst_matieres = []
        for matiere_periode in lst_matiere[periode]:
            lst_notes = []
            for note in raw_notes:
                if note['codeMatiere'] == matiere_periode and note['codePeriode'] == periodes[periode]:
                    if min_max_moy:
                        lst_notes.append((
                            (round((locale.atof(note['minClasse']) * 20) / locale.atof(note['noteSur']), 2),
                              round((locale.atof(note['moyenneClasse']) * 20) / locale.atof(note['noteSur']), 2),
                              round((locale.atof(note['maxClasse']) * 20) / locale.atof(note['noteSur']), 2)),
                                         round((locale.atof(note['valeur']) * 20) / locale.atof(note['noteSur']), 2)))
                    else:
                        lst_notes.append(round((locale.atof(note['valeur']) * 20) / locale.atof(note['noteSur']), 2))
            lst_matieres.append({
                'matiere': matiere_periode,
                'notes': lst_notes
            })

        lst_finale.append({
            'periode': periodes[periode],
            'notes': lst_matieres
        })
    if periode_notes is not None:
        if 0 != int(periode_notes) <= len(lst_finale):
            try:
                lst_finale = [lst_finale[int(periode_notes - 1)]]
            except:
                raise BadPeriode
        else:
            raise BadPeriode

    if matiere is not None:
        try:
            lst_finale2 = []
            for periode in range(len(lst_finale)):
                dic_periode = {'periode': lst_finale[periode]['periode']}
                for a in lst_finale[periode]['notes']:
                    if a['matiere'] == matiere:
                        dic_periode['notes'] = a
                lst_finale2.append(dic_periode)
            lst_finale = lst_finale2
            del lst_finale2
        except:
            raise BadMatiere

    return lst_finale

