package edu.stanford.nlp.pipeline;

import edu.stanford.nlp.util.logging.Redwood;
import edu.stanford.nlp.ling.*;
import edu.stanford.nlp.util.concurrent.MulticoreWrapper;
import edu.stanford.nlp.util.concurrent.ThreadsafeProcessor;

import java.util.*;

public class ProvidedPOSTaggerAnnotator {

  public String tagSeparator;

  public ProvidedPOSTaggerAnnotator(String annotatorName, Properties props) {
    tagSeparator = props.getProperty(annotatorName + ".tagSeparator", "_");
  }

  public void annotate(Annotation annotation) {

    for (CoreLabel token : annotation.get(CoreAnnotations.TokensAnnotation.class)) {
      int tagSeparatorSplitLength = token.word().split(tagSeparator).length;
      String posTag = token.word().split(tagSeparator)[tagSeparatorSplitLength-1];
      String[] wordParts = Arrays.copyOfRange(token.word().split(tagSeparator), 0, tagSeparatorSplitLength-1);
      String tokenString = String.join(tagSeparator, wordParts);
      // set the word with the POS tag removed
      token.set(CoreAnnotations.TextAnnotation.class, tokenString);
      // set the POS
      token.set(CoreAnnotations.PartOfSpeechAnnotation.class, posTag);
    }
  }
}
