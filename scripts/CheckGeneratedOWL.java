import java.nio.file.*;
import java.util.*;
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.profiles.OWL2DLProfile;
import org.semanticweb.owlapi.reasoner.OWLReasoner;
import org.semanticweb.HermiT.ReasonerFactory;

/** Check a complete merged graph without materialising the imported hierarchy. */
public class CheckGeneratedOWL {
    public static void main(String[] args) throws Exception {
        OWLOntologyManager manager = OWLManager.createOWLOntologyManager();
        OWLOntology ontology = manager.loadOntologyFromOntologyDocument(Paths.get(args[0]).toFile());
        boolean profile = new OWL2DLProfile().checkOntology(ontology).isInProfile();
        System.out.println("OWL2DL\t" + profile);
        if (!profile) System.exit(2);
        OWLReasoner reasoner = new ReasonerFactory().createReasoner(ontology);
        boolean consistent = reasoner.isConsistent();
        System.out.println("CONSISTENT\t" + consistent);
        if (args[1].equals("negative")) {
            reasoner.dispose();
            System.exit(consistent ? 1 : 0);
        }
        if (!consistent) System.exit(1);
        int failures = 0;
        List<OWLClass> classes = new ArrayList<>();
        for (OWLClass cls : ontology.getClassesInSignature()) {
            if (cls.getIRI().toString().startsWith("https://w3id.org/ontocal/")) classes.add(cls);
        }
        classes.sort(Comparator.comparing(cls -> cls.getIRI().toString()));
        for (OWLClass cls : classes) {
            boolean satisfiable = reasoner.isSatisfiable(cls);
            System.out.println("SATISFIABLE\t" + cls.getIRI() + "\t" + satisfiable);
            if (!satisfiable) failures++;
        }
        OWLDataFactory factory = manager.getOWLDataFactory();
        List<String> inferred = new ArrayList<>();
        for (String line : Files.readAllLines(Paths.get(args[2]))) {
            String[] fields = line.split("\t");
            boolean expected = Boolean.parseBoolean(fields[0]);
            OWLClassAssertionAxiom axiom = factory.getOWLClassAssertionAxiom(
                factory.getOWLClass(IRI.create(fields[2])),
                factory.getOWLNamedIndividual(IRI.create(fields[1])));
            boolean entailed = reasoner.isEntailed(axiom);
            System.out.println("ENTAILMENT\t" + fields[3] + "\t" + expected + "\t" + entailed);
            if (entailed != expected) failures++;
            if (entailed && !ontology.containsAxiom(axiom))
                inferred.add("<" + fields[1] + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <" + fields[2] + "> .");
        }
        Files.write(Paths.get(args[3]), inferred);
        reasoner.dispose();
        System.exit(failures > 0 ? 1 : 0);
    }
}
