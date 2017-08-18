import disk_test as dt

def run():
	dt.debug_info_en()
	seq = dt.SeqRW('k:', {'MinSectorCnt':32, 'MaxSectorCnt':128})
	seq.WriteDataToDisk('k:', 2131072, 1234)
	seq.ReadDataFromDisk('k:', 2131072, 1234)
	