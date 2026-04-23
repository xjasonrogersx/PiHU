# Test file for updatemd.py

Some introductory text.

## Sequence diagram

![](.img/077301032c23b097c6c61e5518fc5298.png)

<details>
<summary>View UML</summary>

![](.img/077301032c23b097c6c61e5518fc5298.png)
<details>
<summary>View UML</summary>

```uml
Alice -> Bob : hello
Bob --> Alice : hi there
```
</details>

</details>

## Class diagram

![](.img/dc5ba55beb1d8c7342a936047bea87ea.png)

<details>
<summary>View UML</summary>

![](.img/dc5ba55beb1d8c7342a936047bea87ea.png)
<details>
<summary>View UML</summary>

```uml
class Animal {
  +name : string
  +speak() : void
}

class Dog {
  +fetch() : void
}

Animal <|-- Dog
```
</details>

</details>

## Flow diagram / Activity diagram

![](.img/44864c242b77c1e8f6c6803f5f1f41c0.png)

<details>
<summary>View UML</summary>

![](.img/44864c242b77c1e8f6c6803f5f1f41c0.png)
<details>
<summary>View UML</summary>

```uml
start
:Process starts;
if (Condition met?) then (yes)
  :Execute task A;
  :Execute task B;
else (no)
  :Skip tasks;
endif
:Process ends;
stop
```
</details>

</details>

## End

That's all.
