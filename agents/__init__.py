"""Sales agents for the multi-channel adaptive sales system."""

from .classifier import ProspectClassifier
from .seller import SellerAgent
from .negotiator import NegotiatorAgent
from .crm import CRMAgent
from .supervisor import SupervisorAgent

__all__ = [
    "ProspectClassifier",
    "SellerAgent",
    "NegotiatorAgent",
    "CRMAgent",
    "SupervisorAgent",
]
