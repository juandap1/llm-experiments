import { defineStore, acceptHMRUpdate } from 'pinia'

export const useNotesStore = defineStore('notes', {
  state: () => ({
    _activeNote: null,
    _openTabs: [],
    sample: [
      {
        id: 1,
        type: 'folder',
        name: 'Folder Name',
        children: [{ id: 2, type: 'note', name: 'Nested Note 1', content: '' }],
      },
      {
        id: 3,
        type: 'note',
        name: 'Note Name',
        content: `## AWS EC2 Instance: Quick Overview Notes 💻

***

### 1. What is an EC2 Instance?

* **EC2** stands for **Elastic Compute Cloud**.
* It's a web service that provides **secure, resizable compute capacity** in the cloud.
* Essentially, it's a **virtual server** (or instance) you can use to run applications on Amazon's infrastructure.
* It's the core compute resource in **AWS** (Amazon Web Services).

***

### 2. Key Concepts & Features

| Concept | Description |
| :--- | :--- |
| **AMI** (Amazon Machine Image) | A template that includes the operating system, application server, and applications required to launch your instance. |
| **Instance Types** | Various configurations of CPU, memory, storage, and networking capacity (e.g., *t2.micro*, *m5.large*). Choose based on your workload needs. |
| **Security Groups** | Act as a **virtual firewall** for your instance to control inbound and outbound traffic at the instance level. **Crucial for security.** |
| **Key Pair** | Used to securely **SSH** (Secure Shell) into Linux instances or decrypt the administrator password for Windows instances. |
| **EBS** (Elastic Block Store) | Provides **persistent block storage** volumes for use with EC2 instances. It's like a network-attached hard drive. |
| **Elastic IP** | A **static, public IPv4 address** designed for dynamic cloud computing. It's associated with your AWS account and can be quickly remapped to a different instance in case of failure. |

***

### 3. Pricing Models

AWS offers several ways to pay for EC2, allowing cost optimization:

* **On-Demand:** Pay for the compute capacity you use **by the hour or second** with no long-term commitment. Good for irregular workloads.
* **Savings Plans / Reserved Instances (RIs):** Commit to a certain amount of usage (e.g., 1 or 3 years) for a **significant discount** compared to On-Demand. Good for steady-state, predictable workloads.
* **Spot Instances:** Request **unused EC2 capacity** for a very low price. You must be prepared for AWS to terminate the instance if capacity is needed elsewhere. Good for flexible, fault-tolerant workloads.

***

### 4. Basic Use Case Example

* **Need:** Host a public-facing website.
* **Setup:** Launch an EC2 instance using a **Linux AMI**, select an **instance type** (e.g., *t2.small*), attach an **EBS volume** for storage, configure the **Security Group** to allow **HTTP/HTTPS (ports 80/443)** inbound, and install a web server (like Apache or Nginx).`,
      },
      { id: 4, type: 'note', name: 'Note Name 2', content: '' },
    ],
  }),

  getters: {
    noteMap: (state) =>
      state.sample.reduce((map, item) => {
        if (map[item.id] == null) map[item.id] = item
        state.recursivelyMap(map, item, 'children')
        return map
      }, {}),
    activeNoteData: (state) => {
      return state.noteMap[state._activeNote] || null
    },
  },

  actions: {
    recursivelyMap(map, item, prop) {
      if (item[prop] != null && Array.isArray(item[prop])) {
        item[prop].forEach((child) => {
          map[child.id] = child
          this.recursivelyMap(map, child, prop)
        })
      }
    },
    setActiveNote(id) {
      this._activeNote = id
      this._openTabs[0] = id
    },
  },
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useNotesStore, import.meta.hot))
}
