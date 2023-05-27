import glob
import os


class Testset:
    def __init__(self, basepath, dataset, lp):
        self.basepath = basepath
        self.dataset = dataset
        self.lp = lp

        self.doc_ids = []
        self.sources = []
        self.references = {}
        self.systems = {}
        self.documents = []
        self.main_ref = None

        self.load()


    def load(self):
        dataset = f"{self.basepath}/{self.dataset}"

        # get doc ids used for adding preceding context sentences
        self.doc_ids = self.load_doc_ids(f"{dataset}/documents/{self.lp}.docs")

        self.sources = self.load_segment_files(f"{dataset}/sources/{self.lp}.txt")

        # list all files in references folder
        refs = glob.glob(f"{dataset}/references/{self.lp}.*.txt")
        for reffile in refs:
            refname = reffile.split('.')[-2]
            if self.main_ref is None:
                self.main_ref = refname
            self.references[refname] = self.load_segment_files(reffile)

        systems = f"{dataset}/system-outputs/{self.lp}"
        # keep systems in order
        all_systems = sorted(os.listdir(systems))
        for system in all_systems:
            systemname = system.replace(".txt", "")
            self.systems[systemname] = self.load_segment_files(f"{systems}/{system}")

        self.documents = self.load_docs(f"{dataset}/documents/{self.lp}.docs")


    def iterate_over_all(self, reference=None):
        for system in self.systems.keys():
            if reference is None:
                for src, hyp in zip(self.sources, self.systems[system]):
                    yield src, hyp, None, system
            else:
                for src, hyp, ref in zip(self.sources, self.systems[system], self.references[reference]):
                    yield src, hyp, ref, system


    def load_segment_files(self, path):
        segments = []
        with open(path, "r") as fh:
            for line in fh:
                segments.append(line.rstrip())
        # add 2 previous context sentences
        segments = self.add_context(segments, segments, self.doc_ids, ws=2)
        return segments


    def load_doc_ids(self, path):
        '''Get document ids from document files'''
        with open(path, "r") as fh:
            lines = [line.split('\t') for line in fh]
            doc_ids = [line[1].strip() for line in lines]
        return doc_ids
    

    def load_docs(self, path):
        '''Load document files (contains domain and doc id)'''
        with open(path, "r") as fh:
            docs = [line.rstrip() for line in fh]
        return docs

    
    def add_context(self, orig_txt, context, doc_ids, ws=2):
        '''Add preceding context sentences considering document boundaries'''
        assert len(orig_txt) == len(context) == len(doc_ids), "Length of original text, context and doc ids doesn't match"
        i, k = 0, 0
        augm_txt = []
        doc_id = doc_ids[0]
        while i < len(orig_txt):
            if doc_ids[i] == doc_id:
                context_window = context[i - min(k, ws):i]
                augm_txt.append(" ".join(context_window + [orig_txt[i]]))
                i += 1
            else:
                doc_id = doc_ids[i]
                k = -1
            k += 1
        return augm_txt


    def segments_count(self):
        return len(self.sources)*len(self.systems)