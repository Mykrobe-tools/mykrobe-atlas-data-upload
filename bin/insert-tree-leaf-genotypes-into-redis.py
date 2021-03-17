import redis
from bitarray import bitarray

REDIS_HOST = "redis"
REDIS_PORT = 6379

REDIS = redis.StrictRedis(REDIS_HOST, REDIS_PORT, db=4)
GENOTYPE_KEY = "genotype"
GENOTYPE_TREE_LEAVE_KEY = "genotype-tree-leaves"

counter = 0
with open("tree-leaf-genotype-calls") as infile:
    for line in infile:
        line = line.strip()
        tree_leaf_name, genotype_calls = line.split(sep="\t")
        num_calls = len(genotype_calls)
        key1 = f"{GENOTYPE_KEY}-homozygous-{tree_leaf_name}"
        key2 = f"{GENOTYPE_KEY}-alternate-{tree_leaf_name}"
        homozygous = bitarray(num_calls)
        homozygous.setall(0)
        alternate = bitarray(num_calls)
        alternate.setall(0)
        for index, genotype_call in enumerate(genotype_calls):
            if genotype_call == "1":
                homozygous[index] = 1
            if genotype_call == "2":
                homozygous[index] = 1
                alternate[index] = 1
        pipe = REDIS.pipeline()
        for index, bit in enumerate(homozygous):
            if bit:
                pipe.setbit(key1, index, 1)
        for index, bit in enumerate(alternate):
            if bit:
                pipe.setbit(key2, index, 1)
        pipe.sadd(GENOTYPE_TREE_LEAVE_KEY, tree_leaf_name)
        pipe.execute()
        counter = counter + 1
        if counter % 100 == 0:
            print(f"completed {counter} lines")

print("complete!")
