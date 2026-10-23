class Tutor {
  final int? id;
  final String name;
  final String email;
  final List<String> subjects;
  final int expertiseLevel;
  final String teachingPreference;
  final List<String> availability;

  Tutor({
    this.id,
    required this.name,
    required this.email,
    required this.subjects,
    required this.expertiseLevel,
    required this.teachingPreference,
    required this.availability,
  });

  Map<String, dynamic> toJson() => {
        "name": name,
        "email": email,
        "subjects": subjects,
        "expertise_level": expertiseLevel,
        "teaching_preference": teachingPreference,
        "availability": availability,
      };

  factory Tutor.fromJson(Map<String, dynamic> json) => Tutor(
        id: json["id"],
        name: json["name"],
        email: json["email"],
        subjects: List<String>.from(json["subjects"] ?? []),
        expertiseLevel: json["expertise_level"],
        teachingPreference: json["teaching_preference"],
        availability: List<String>.from(json["availability"] ?? []),
      );
}


/// Result item returned by GET /api/matches/{learner_id}.
/// Contains tutor details, compatibility breakdown, and ML scoring information.
class TutorMatch {
  final int tutorId;
  final String name;
  final List<String> subjects;
  final String teachingPreference;
  final List<String> availability;

  // Existing compatibility score
  final double compatibilityScore;

  // New ML recommendation fields
  final double matchScore;
  final String scoringMethod;
  final double? mlMatchProbability;
  final String? fallbackReason;

  // Score breakdown from the backend
  final Map<String, dynamic> breakdown;

  TutorMatch({
    required this.tutorId,
    required this.name,
    required this.subjects,
    required this.teachingPreference,
    required this.availability,
    required this.compatibilityScore,
    required this.matchScore,
    required this.scoringMethod,
    this.mlMatchProbability,
    this.fallbackReason,
    required this.breakdown,
  });

  factory TutorMatch.fromJson(Map<String, dynamic> json) {
    return TutorMatch(
      tutorId: (json["tutor_id"] as num).toInt(),
      name: json["name"] as String,
      subjects: List<String>.from(json["subjects"] ?? []),
      teachingPreference: json["teaching_preference"] as String,
      availability: List<String>.from(json["availability"] ?? []),

      compatibilityScore:
          (json["compatibility_score"] as num).toDouble(),

      matchScore: (json["match_score"] as num?)?.toDouble() ??
          (json["compatibility_score"] as num).toDouble(),

      scoringMethod: json["scoring_method"] as String? ?? "fallback",

      mlMatchProbability:
          (json["ml_match_probability"] as num?)?.toDouble(),

      fallbackReason: json["fallback_reason"] as String?,

      breakdown: Map<String, dynamic>.from(
        json["breakdown"] ?? {},
      ),
    );
  }
}
