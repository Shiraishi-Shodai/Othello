import datetime
import csv


FORMAT = 'iso-8859-2'
RECORD_BYTES = {'header': 16, 'jou': 20, 'trn': 26}
MAX_MOVES = 60


class Wthor:
    def __init__(self, jou='WTHOR.JOU', trn='WTHOR.TRN', wtb='WTH_2022.wtb'):
        self.players = self._get_records(jou, RECORD_BYTES['jou'])
        self.tournaments = self._get_records(trn, RECORD_BYTES['trn'])
        self.games = self._get_games(wtb)

    def _get_records(self, filename, rbytes):
        ret = []
        with open(filename, 'rb') as f:
            f.read(RECORD_BYTES['header'])  # discard header
            for _ in range(self._decode_header(filename)['records']):
                ret.append(f.read(rbytes).decode(FORMAT).replace('\x00', ''))
        return ret

    def _get_games(self, wtb):
        ret = []
        header = self._decode_header(wtb)
        with open(wtb, 'rb') as f:
            f.read(RECORD_BYTES['header'])  # discard header
            for _ in range(header['game_count']):
                ret.append({
                    'match_year': header['match_year'],
                    'tournament': self.tournaments[self._byte2int(f.read(2))],
                    'black': self.players[self._byte2int(f.read(2))],
                    'white': self.players[self._byte2int(f.read(2))],
                    'board_size': header['board_size'],
                    'black_score': self._byte2int(f.read(1)),
                    'theoretical': self._byte2int(f.read(1)),
                    'depth': header['depth'],
                    'record': self._get_record(f),
                })
        return ret

    def _get_record(self, f):
        ret = ""
        for _ in range(MAX_MOVES):
            move = str(self._byte2int(f.read(1)))
            if len(move) == 2:
                ret += chr(ord('a') + int(move[1]) - 1) + move[0]
        return ret

    def _decode_header(self, dbname):
        with open(dbname, 'rb') as f:
            return {
                'created_date': self._get_created_date(f),
                'game_count': self._byte2int(f.read(4)),
                'records': self._byte2int(f.read(2)),
                'match_year': self._byte2int(f.read(2)),
                'board_size': self._byte2int(f.read(1)),
                'match_type': self._byte2int(f.read(1)),
                'depth': self._byte2int(f.read(1)),
            }

    def _get_created_date(self, f):
        y = str(self._byte2int(f.read(1))) + str(self._byte2int(f.read(1)))
        m = str(self._byte2int(f.read(1)))
        d = str(self._byte2int(f.read(1)))
        return datetime.datetime.strptime('-'.join([y, m, d]), '%Y-%m-%d')

    def _byte2int(self, byte, byteorder='little'):
        return int.from_bytes(byte, byteorder=byteorder)

    def to_csv(self, csv_file='output.csv'):
        header = [
            'Match Year', 'Tournament Name', 'Black Player Name',
            'White Player Name', 'Board Size', 'Black Score',
            'Black Theoretical Score', 'Depth', 'Record',
        ]
        with open(csv_file, 'w', newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for game in self.games:
                writer.writerow(game.values())


if __name__ == '__main__':
    Wthor(
        jou="datasets/WTHOR.JOU",
        trn="datasets/WTHOR.TRN",
        wtb="datasets/WTH_2025.wtb").to_csv()