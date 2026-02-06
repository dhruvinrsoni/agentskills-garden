# Human Review Checklist for AgentSkills

Use this checklist when manually evaluating a new or updated skill. This serves as the final validation layer in our three-tiered testing pyramid.

## Skill Information

- **Skill ID:** `_____________________`
- **Version:** `_____________________`
- **Reviewer:** `_____________________`
- **Date:** `_____________________`

---

## 1. Correctness ✓

- [ ] The skill produces correct outputs for typical inputs
- [ ] The skill handles edge cases appropriately
- [ ] Error messages are clear and actionable
- [ ] The skill behaves deterministically (same input → same output)

**Notes:**
```
```

---

## 2. Utility & Relevance 🎯

- [ ] The skill addresses a real need in the target domain
- [ ] The skill's outputs are actionable and useful
- [ ] The skill provides value beyond what a basic LLM can do
- [ ] The skill bridges one of the 7 capability gaps effectively

**Notes:**
```
```

---

## 3. Interface Design 🔌

- [ ] Input schema is clear and well-documented
- [ ] Output schema is structured and parseable
- [ ] Required vs optional parameters are intuitive
- [ ] Context requirements are minimal and justified

**Notes:**
```
```

---

## 4. Documentation Quality 📚

- [ ] `schema.json` is complete and accurate
- [ ] `README.md` has clear usage examples
- [ ] Code has helpful comments for maintainers
- [ ] Error scenarios are documented

**Notes:**
```
```

---

## 5. Performance ⚡

- [ ] Execution completes in reasonable time (< 30s for typical use)
- [ ] Memory usage is acceptable
- [ ] Token consumption (if using LLM) is justified
- [ ] No obvious performance bottlenecks

**Notes:**
```
```

---

## 6. Reliability 🛡️

- [ ] The skill has comprehensive unit tests
- [ ] Edge cases and error paths are tested
- [ ] The skill fails gracefully with clear messages
- [ ] Dependencies are stable and well-maintained

**Notes:**
```
```

---

## 7. Integration 🔗

- [ ] The skill works standalone (can be tested in isolation)
- [ ] The skill integrates with declared dependencies correctly
- [ ] The skill follows the HTTP contract specification
- [ ] The skill can be composed with other skills

**Notes:**
```
```

---

## 8. Security & Safety 🔒

- [ ] Input validation prevents injection attacks
- [ ] The skill doesn't leak sensitive information
- [ ] File/network access is scoped appropriately
- [ ] Resource limits prevent DoS scenarios

**Notes:**
```
```

---

## Overall Assessment

### Strengths
```
1. 
2. 
3. 
```

### Areas for Improvement
```
1. 
2. 
3. 
```

### Recommendation

- [ ] ✅ Approve for release
- [ ] 🚧 Approve with minor fixes
- [ ] ❌ Requires major revisions
- [ ] 🔄 Re-review after changes

### Final Comments
```


```

---

**Reviewer Signature:** `_____________________`  
**Date:** `_____________________`
