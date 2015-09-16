from corpsearchsystem import CorpSearchSystem

from modules.editdistance.normalized import \
    NormalizedEditDistanceQueryToHandle,\
    NormalizedEditDistanceQueryToDisplayName
from modules.editdistance.lengths import \
    LengthOfQuery, LengthOfHandle, LengthOfDisplayName
from modules.editdistance.stopwords import \
    NormalizedEditDistanceStopwordsQueryToHandle,\
    NormalizedEditDistanceStopwordsQueryToDisplayName

from modules.description.counts import OccurrencesOfQueryInDescCaseInsensitive
from modules.description.cosinesimilarity import \
    CosineSimilarityDescriptionAndQuery, \
    CosineSimilarityDescriptionAndDDG

from modules.languagemodels.bigram import \
    DescriptionLanguageModel, \
    PostContentLanguageModel

Baseline = CorpSearchSystem('Baseline', [
        NormalizedEditDistanceStopwordsQueryToHandle,
        NormalizedEditDistanceStopwordsQueryToDisplayName
    ])

# Baseline plus x.
PlusLengths = CorpSearchSystem('+ Lengths', [
        NormalizedEditDistanceStopwordsQueryToHandle,
        NormalizedEditDistanceStopwordsQueryToDisplayName,
        LengthOfQuery,
        LengthOfHandle,
        LengthOfDisplayName
    ])

PlusQueryOccurrences = CorpSearchSystem('+ Query Occurrences', [
        NormalizedEditDistanceStopwordsQueryToHandle,
        NormalizedEditDistanceStopwordsQueryToDisplayName,
        OccurrencesOfQueryInDescCaseInsensitive
    ])

PlusDescriptionCosineSimilarity = CorpSearchSystem(
    '+ Description-Query Cosine Similarity', [
        NormalizedEditDistanceStopwordsQueryToHandle,
        NormalizedEditDistanceStopwordsQueryToDisplayName,
        CosineSimilarityDescriptionAndQuery
    ])

PlusDescriptionDDGCosineSimilarity = CorpSearchSystem(
    '+ Description-DDG Cosine Similarity', [
        NormalizedEditDistanceStopwordsQueryToHandle,
        NormalizedEditDistanceStopwordsQueryToDisplayName,
        CosineSimilarityDescriptionAndDDG
    ])

PlusDescriptionLanguageModels = CorpSearchSystem(
    '+ Description Language Models', [
        NormalizedEditDistanceStopwordsQueryToHandle,
        NormalizedEditDistanceStopwordsQueryToDisplayName,
        DescriptionLanguageModel
    ])

PlusPostContentLanguageModels = CorpSearchSystem(
    '+ Post Content Language Models', [
        NormalizedEditDistanceStopwordsQueryToHandle,
        NormalizedEditDistanceStopwordsQueryToDisplayName,
        PostContentLanguageModel
    ])
# End Baseline plus x.

Final = CorpSearchSystem('Production System', [
        NormalizedEditDistanceStopwordsQueryToHandle,
        NormalizedEditDistanceStopwordsQueryToDisplayName,
        LengthOfQuery,
        LengthOfHandle,
        LengthOfDisplayName,
        OccurrencesOfQueryInDescCaseInsensitive,
        CosineSimilarityDescriptionAndQuery,
        CosineSimilarityDescriptionAndDDG,
        DescriptionLanguageModel,
        PostContentLanguageModel
    ])
