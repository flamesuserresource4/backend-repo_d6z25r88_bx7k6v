"""
Database Schemas for I LOVE HIP HOP JA

Each Pydantic model represents a MongoDB collection. The collection name is the
lowercase of the class name (e.g., Member -> "member").
"""
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime

# Core domain schemas

class Member(BaseModel):
    email: str = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    ig_handle: Optional[str] = Field(None, description="Instagram handle")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    tier: str = Field("standard", description="Membership tier")
    saved_mixtapes: List[str] = Field(default_factory=list)
    saved_photos: List[str] = Field(default_factory=list)
    music_favorites_songs: List[str] = Field(default_factory=list)
    music_favorites_albums: List[str] = Field(default_factory=list)
    music_favorites_lyrics: List[str] = Field(default_factory=list)
    favorite_djs: List[str] = Field(default_factory=list)

class RSVP(BaseModel):
    name: str = Field(..., description="Full name of the person reserving")
    email: str = Field(..., description="Email for confirmation")
    phone: Optional[str] = Field(None)
    package: str = Field(..., description="Package type: Special, VIP, Mogul")
    group_size: int = Field(2, ge=1, le=20)
    bottle_choice: Optional[str] = None
    notes: Optional[str] = None
    status: str = Field("pending", description="pending|confirmed|cancelled|completed")

class Event(BaseModel):
    title: str
    slug: Optional[str] = None
    date: datetime
    theme: Optional[str] = None
    description: Optional[str] = None
    flyer_url: Optional[str] = None
    sponsors: List[str] = Field(default_factory=list)
    djs: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    is_featured: bool = False
    venue_name: Optional[str] = None
    venue_address: Optional[str] = None

class Article(BaseModel):
    title: str
    slug: str
    content: str
    tags: List[str] = Field(default_factory=list)
    author: Optional[str] = None
    cover_image: Optional[HttpUrl] = None

class Mixtape(BaseModel):
    title: str
    dj: str
    embed_url: Optional[HttpUrl] = None
    cover_image: Optional[HttpUrl] = None
    description: Optional[str] = None
    external_url: Optional[HttpUrl] = None
    plays: int = 0

class Partner(BaseModel):
    name: str
    logo_url: Optional[HttpUrl] = None
    instagram: Optional[str] = None
    gallery_url: Optional[HttpUrl] = None
    featured: bool = False

class Coupon(BaseModel):
    code: str
    title: str = Field("Happy Hour 8:00–10:30 PM")
    member_only: bool = False
    starts_at: datetime
    ends_at: datetime

class Special(BaseModel):
    title: str = Field("2-4-1 Specials")
    details: str = Field("Members get 2-for-1 drinks this week")
    week_of: datetime

# Note: Additional collections (e.g., Profile) can be added later. The Member model
# already carries the cultural identity preferences.
