import collections

def getOverlap(a, b):
    return max(0, min(a[1], b[1]) - max(a[0], b[0]))

class repository: 
    def __init__(self, policy = None, title = None, chapter = None, section = None, article = None, sentence = None, index_name = None):
        self.policy = policy
        self.title = title
        self.chapter = chapter
        self.section = section
        self.article = article
        self.sentence = sentence
        self.index_name = index_name # the name of the repository used by the dataframe as index

    def __repr__(self): #how to print the repository to the console
        return f"policy:{self.policy} title:{self.title} chapter:{self.chapter} section:{self.section} article:{self.article}" + (f"sentence:{self.sentence}" if self.sentence != None else '')
   
    def __eq__(self, other):
        if isinstance(other, repository):
            return self.policy == other.policy and self.title == other.title and self.chapter == other.chapter and self.section == other.section and self.article == other.article and self.sentence == self.sentence
        return False
        
    def __hash__(self):
        return hash(self.__repr__())


    @classmethod
    def from_repository_name(cls, rep_str):                #2nd initializer that creates a repository object directly from a repository string e.g 'EU_32008R1099_Title_0_Chapter_0_Section_0_Article_03.txt'
        folder_parts = rep_str.split('_')                  #split the string at '_' into parts 
        policy = folder_parts[0] + '_' + folder_parts[1]   #we only want to split at every 2nd '_', so merge the 1. and 2., 3. and 4. again 
        
        if folder_parts[2] in  ['front', 'Whereas']:       #exeption for the 'whereas' and 'front'
            title = folder_parts[2]
            chapter = None
            section = None
            article = None
            sentence = None
        else:
            title = folder_parts[2] + '_' + folder_parts[3]
            chapter = folder_parts[4] + '_' + folder_parts[5]
            section = folder_parts[6] + '_' + folder_parts[7]
            article = folder_parts[8] + '_' + folder_parts[9]
            

            if len(folder_parts) == 12:
                sentence = folder_parts[10] + '_' + folder_parts[11]
            else:
                sentence = None
        
        return cls(policy,title, chapter, section, article, sentence, rep_str)  #return a repository with the previously defined attributes
    
    def match(self, other):            #checks if the search-criteria defined in repository 'other' is matching the the current repository                                                
        self_value_set = set([x for x in list(self.__dict__.values()) if x != None]) #creates a set of all the attributes ignoring 'None'    
        other_value_set = set([x for x in list(other.__dict__.values()) if x != None])
        
        return set(other_value_set).issubset(self_value_set) #returns True if the attributes of the search-criteria is a subset of the attributes of the current directory (=match)
    
class token:
    def __init__(self, start, stop, text, rep, tag_count = 0):
        self.start = start
        self.stop = stop
        self.text = text
        self.rep = rep
        self.tag_count = tag_count
        
    def __repr__(self):
        return f"start:{self.start} stop:{self.stop} text:{self.text} tag_count:{self.tag_count}"

    def __hash__(self): # used to remove duplicates
        return hash(self.__repr__())
        
class span:
    def __init__(self, span_id = None, layer_ = None, type_ = None, tag_ = None, start = None, stop = None, text = None, tokens = None, rep = None, annotator = None):
        self.span_id = span_id
        self.layer_ = layer_
        self.type_ = type_
        self.tag_ = tag_
        self.start = start
        self.stop = stop
        self.text = text
        self.tokens = tokens
        self.rep = rep
        self.annotator = annotator

    
    #def __del__(self):
    #    print('Span ', self.span_id, ' was removed from the corpus')

    def __eq__(self, other): 
        if isinstance(other, span):
                # don't attempt to compare against unrelated types
            return self.span_id == other.span_id
        return False

    
    def __repr__(self): #for debugging purpose, defines how object is printed
        return f"span id:{self.span_id} annotator:{self.annotator} layer:{self.layer_} type:{self.type_} tag:{self.tag_} start:{self.start} stop:{self.stop} text:{self.text}"

    def __hash__(self):
        return hash((self.annotator, self.layer_, self.type_, self.tag_, self.start, self.stop, self.text, self.rep.__hash__()))  #tags with identical properties and identical repo shoudl yield the same hash so they can be removed

    def get_start(self):
        return self.start

    def exact_match(self, other):
        return self.start == other.start and self.stop == other.stop and self.tag_ == other.tag_

    def partial_match(self, other):

        return self.start < other.stop and other.start < self.stop and self.tag_ == other.tag_
    
    def tokenwise_f1_score(self, other):
        if self.tag_ != other.tag_:
            return 0
        if self.tag_ == None or other.tag_ == None:
            return 0
        if self.tag_ == other.tag_:
            if len(self.tokens) == 0 or len(other.tokens) == 0:
                #if either is no answer, return 1 if they agree, zero else
                return int(self.tokens == other.tokens)

            common = collections.Counter(self.tokens) & collections.Counter(other.tokens)
            num_same = sum(common.values())

            if num_same == 0:
                return 0
                
            precision = 1.0 * num_same / len(self.tokens)
            recall = 1.0 * num_same / len(other.tokens)
            f1 = (2*precision * recall) / (precision + recall)
            return f1
        else:
            raise ValueError('None of the mentioned')




